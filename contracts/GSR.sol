pragma solidity ^0.4.24;

import "./Ownable.sol";
import "./GEO.sol";
import "./math/SafeMath8.sol";
import "./math/SafeMath.sol";
import "./math/SafeMath16.sol";

contract GSR is Ownable {
    using SafeMath8 for uint8;
    using SafeMath16 for uint16;
    using SafeMath for uint256;

    GEO public geo;

    // (sha3(registry name)) => (epoch) => (address) => (vote token amount)
    mapping(bytes32 => mapping(uint16 => mapping(address => uint256))) private registry;
    mapping(address => uint256) public stake;
    mapping(address => uint256) public stakeLockup;
    // bytes32 << keccak256(registry name)
    mapping(bytes32 => bool) public registryName;
    mapping(bytes32 => uint256) private totalVotesForNewRegistry;
    mapping(bytes32 => mapping(address => uint256)) private votesForNewRegistry;
    mapping(address => bytes32[]) private haveVotesForNewRegistry;

    uint16 public currentEpoch;
    uint256 private epochTimeLimit;
    uint256 private epochTime;

    modifier registryExist(string _name)
    {
        require(registryName[keccak256(_name)]);
        _;
    }

    modifier haveStake()
    {
        require(stake[msg.sender] > 0);
        if (stakeLockup[msg.sender] > 0)
            require(geo.lockupExpired() > now);
        _;
    }

    constructor() public {
        epochTimeLimit = 7 days;
        currentEpoch = 0;
        restartEpochTime();
    }

    function voteForNewRegistry(string _name)
    haveStake()
    public
    {
        require(registryName[keccak256(_name)] == false);
        bytes32 registryHashName = keccak256(_name);
        if (votesForNewRegistry[registryHashName][msg.sender] == 0) {
            haveVotesForNewRegistry[msg.sender].push(registryHashName);
        }
        totalVotesForNewRegistry[registryHashName] -= votesForNewRegistry[registryHashName][msg.sender];
        totalVotesForNewRegistry[registryHashName] += stake[msg.sender];
        votesForNewRegistry[registryHashName][msg.sender] = stake[msg.sender];
        if (totalVotesForNewRegistry[registryHashName] >= geo.totalSupply() / 10) {
            registryName[registryHashName] = true;
            //            delete totalVotesForRegistryName[registryHashName];
            //            delete votesForRegistryName[registryHashName]; can't delete this
        }
    }

    function cancelVoteForNewRegistry()
    private
    {
        bytes32[] memory hashesForRegistryNames = haveVotesForNewRegistry[msg.sender];
        for (uint256 v = 0; v < hashesForRegistryNames.length; v++) {
            if (!registryName[hashesForRegistryNames[v]]) {
                totalVotesForNewRegistry[hashesForRegistryNames[v]] -= votesForNewRegistry[hashesForRegistryNames[v]][msg.sender];
                votesForNewRegistry[hashesForRegistryNames[v]][msg.sender] = 0;
            }
        }
    }

    function vote(string _registryName, address _candidate)
    registryExist(_registryName)
    haveStake()
    public
    {
    }

    function cancelVote(string _registryName)
    registryExist(_registryName)
    public
    {

    }

    function voteService(uint256 _amount)
    public
    {
        require(geo.lockupExpired() < now);
        if (stakeLockup[msg.sender] > 0) {
            stakeLockup[msg.sender] = 0;
            stake[msg.sender] = 0;
        }
        stake[msg.sender] = stake[msg.sender].add(_amount);
        geo.transferFrom(msg.sender, address(this), _amount);
    }

    function voteServiceLockup(uint256 _amount)
    public
    {
        require(geo.lockupExpired() > now);
        stake[msg.sender] = stake[msg.sender].add(_amount);
        if (stake[msg.sender] > geo.balanceOf(msg.sender)) {
            stake[msg.sender] = geo.balanceOf(msg.sender);
        }
        stakeLockup[msg.sender] = stake[msg.sender];
    }

    function withdraw()
    public
    {
        cancelVoteForNewRegistry();
        if (stakeLockup[msg.sender] == 0) {
            geo.transfer(msg.sender, stake[msg.sender]);
        }
        stake[msg.sender] = 0;
        stakeLockup[msg.sender] = 0;
    }

    /**
    * @dev Check and change number of current epoch
    */
    function checkEpoch()
    private
    returns (uint16)
    {
        if (epochTime < now) {
            return increaseEpoch();
        }
    }

    /**
    * @dev Increase current epoch
    */
    function increaseEpoch()
    private
    returns (uint16)
    {
        restartEpochTime();
        currentEpoch = uint16(currentEpoch.add(1));
        return currentEpoch;
    }

    /**
    * @dev Start time from now
    */
    function restartEpochTime()
    private
    {
        epochTime = now.add(epochTimeLimit);
    }

}
