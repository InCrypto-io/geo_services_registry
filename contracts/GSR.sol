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
    mapping(bytes32 => uint256) public totalVotesForRegistryName;
    mapping(bytes32 => mapping(address => uint256)) public votesForRegistryName;
    mapping(address => bytes32[]) public haveVotesForRegistryNames;

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
        _;
    }

    constructor() public {
        epochTimeLimit = 7 days;
        currentEpoch = 0;
        restartEpochTime();
    }

    function voteForRegistry(string _name)
    haveStake()
    public
    {
        require(registryName[keccak256(_name)] == false);
        bytes32 registryHashName = keccak256(_name);
        if (votesForRegistryName[registryHashName][msg.sender] == 0) {
            haveVotesForRegistryNames[msg.sender].push(registryHashName);
        }
        totalVotesForRegistryName[registryHashName] -= votesForRegistryName[registryHashName][msg.sender];
        totalVotesForRegistryName[registryHashName] += stake[msg.sender];
        votesForRegistryName[registryHashName][msg.sender] = stake[msg.sender];
        if (totalVotesForRegistryName[registryHashName] >= geo.totalSupply() / 10) {
            registryName[registryHashName] = true;
//            delete totalVotesForRegistryName[registryHashName];
//            delete votesForRegistryName[registryHashName]; can't delete this
        }
    }

    function vote(string _registryName)
    registryExist(_registryName)
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

    }

    function voteServiceLockup(uint256 _amount)
    public
    {

    }

    function withdraw()
    public
    {

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
