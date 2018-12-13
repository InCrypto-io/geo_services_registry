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

    mapping(address => uint256) public stake;
    mapping(address => uint256) public stakeLockup;

    mapping(bytes32 => mapping(uint16 => address[])) public candidatesListInRegistries;
    // (keccak256(registry name)) => (epoch) => (candidate address) => (is candidate)
    mapping(bytes32 => mapping(uint16 => mapping(address => bool))) private isCandidateInCurrentEpoch;
    // (keccak256(registry name)) => (epoch) => (candidate address) => (total votes amount)
    mapping(bytes32 => mapping(uint16 => mapping(address => uint256))) private totalTokensForCandidate;
    // (keccak256(registry name)) => (epoch) => (voter address) => (vote amount)
    mapping(bytes32 => mapping(uint16 => mapping(address => uint256))) private amountTokenForCandidateFromVoter;
    // (keccak256(registry name)) => (epoch) => (voter address) => (candidate address)
    mapping(bytes32 => mapping(uint16 => mapping(address => address))) private candidateForVoter;

    // bytes32 << keccak256(registry name)
    mapping(bytes32 => bool) private registryName;
    mapping(bytes32 => uint256) private totalVotesForNewRegistry;
    mapping(bytes32 => mapping(address => uint256)) private votesForNewRegistry;
    mapping(address => bytes32[]) private haveVotesForNewRegistry;
    string[] public registryList;

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

    constructor(address _geoAddress) public {
        geo = GEO(_geoAddress);
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
            registryList.push(_name);
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
        checkEpoch();
        bytes32 registryHashName = keccak256(_registryName);
        address oldCandidate = candidateForVoter[registryHashName][currentEpoch][msg.sender];
        totalTokensForCandidate[registryHashName][currentEpoch][oldCandidate] -= amountTokenForCandidateFromVoter[registryHashName][currentEpoch][msg.sender];
        totalTokensForCandidate[registryHashName][currentEpoch][_candidate] += stake[msg.sender];
        amountTokenForCandidateFromVoter[registryHashName][currentEpoch][msg.sender] = stake[msg.sender];
        candidateForVoter[registryHashName][currentEpoch][msg.sender] = _candidate;
    }

    function cancelVote(string _registryName)
    registryExist(_registryName)
    haveStake()
    public
    {
        checkEpoch();
        bytes32 registryHashName = keccak256(_registryName);
        address candidate = candidateForVoter[registryHashName][currentEpoch][msg.sender];
        uint256 amountTokens = amountTokenForCandidateFromVoter[registryHashName][currentEpoch][msg.sender];
        if (amountTokens > 0) {
            totalTokensForCandidate[registryHashName][currentEpoch][candidate] -= amountTokens;
            amountTokenForCandidateFromVoter[registryHashName][currentEpoch][msg.sender] = 0;
            candidateForVoter[registryHashName][currentEpoch][msg.sender] = 0;
        }
    }

    function cancelVotes()
    haveStake()
    public
    {
        checkEpoch();
        for (uint256 i = 0; i < registryList.length; i++) {
            cancelVote(registryList[i]);
        }
    }

    function voteService(uint256 _amount)
    public
    {
        checkEpoch();
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
        checkEpoch();
        require(geo.lockupExpired() > now);
        stake[msg.sender] = stake[msg.sender].add(_amount);
        if (stake[msg.sender] > geo.balanceOf(msg.sender)) {
            stake[msg.sender] = geo.balanceOf(msg.sender);
        }
        stakeLockup[msg.sender] = stake[msg.sender];
    }

    function withdraw()
    haveStake()
    public
    {
        checkEpoch();
        cancelVoteForNewRegistry();
        cancelVotes();
        if (stakeLockup[msg.sender] == 0) {
            geo.transfer(msg.sender, stake[msg.sender]);
        }
        stake[msg.sender] = 0;
        stakeLockup[msg.sender] = 0;
    }

    function getCandidatesList(string _registryName, uint16 _epoch)
    view
    public
    returns (address[])
    {
        return candidatesListInRegistries[keccak256(_registryName)][_epoch];
    }

    function getTotalTokensVotedForCandidate(
        string _registryName,
        uint16 _epoch,
        address _candidate)
    view
    public
    returns (uint256)
    {
        return totalTokensForCandidate[keccak256(_registryName)][_epoch][_candidate];
    }

    function isRegistryExist(string _name)
    view
    public
    returns (bool)
    {
        return registryName[keccak256(_name)];
    }

    function getTotalVotesForNewRegistry(string _name)
    view
    public
    returns (uint256)
    {
        return totalVotesForNewRegistry[keccak256(_name)];
    }

    /**
    * @dev Check and change number of current epoch
    */
    function checkEpoch()
    public
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
