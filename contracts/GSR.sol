pragma solidity ^0.4.24;

import "./GEOToken.sol";
import "./math/SafeMath8.sol";
import "./math/SafeMath.sol";
import "./math/SafeMath16.sol";

contract GeoServiceRegistry {

    using SafeMath8 for uint8;
    using SafeMath16 for uint16;
    using SafeMath for uint256;

    /* STORAGE
    */

    GEOToken public token;

    mapping(address => uint256) public stake;
    mapping(address => uint256) public stakeLockup;

    // (keccak256(registry name)) => (epoch) => (candidate address) => (total votes amount)
    mapping(string => mapping(uint16 => mapping(address => uint256))) private totalTokensForCandidate;
    // (keccak256(registry name)) => (epoch) => (voter address) => (vote amount)
    mapping(string => mapping(uint16 => mapping(address => uint256))) private amountTokenForCandidateFromVoter;
    // (keccak256(registry name)) => (epoch) => (voter address) => (candidate address)
    mapping(string => mapping(uint16 => mapping(address => address))) private candidateForVoter;

    mapping(string => bool) private registryName;
    mapping(string => uint256) private totalVotesForNewRegistry;
    mapping(string => mapping(address => uint256)) private votesForNewRegistry;
    mapping(address => string[]) private haveVotesForNewRegistry;
    string[] public registryList; // todo due to code review -- remove

    uint16 public currentEpoch;
    uint16 private voteForEpoch;
    uint256 private epochTimeLimit;
    uint256 private epochZero;

    /* EVENTS
    */

    event NewEpoch(uint256 _number);
    event NewRegistry(string _name);

    /* MODIFIERS
    */

    modifier registryExist(string _name)
    {
        require(registryName[_name]);
        _;
    }

    /* CONSTRUCTOR
    */

    constructor(address _geoAddress)
    public
    {
        token = GEOToken(_geoAddress);
        epochTimeLimit = 7 days;
        currentEpoch = 0;
        voteForEpoch = 1;
        epochZero = now;
    }

    /* FUNCTIONS
    */

    function voteForNewRegistry(string _registryName)
    public
    {
        require(registryName[_registryName] == false);
        if (votesForNewRegistry[_registryName][msg.sender] == 0) {
            haveVotesForNewRegistry[msg.sender].push(_registryName);
        }
        totalVotesForNewRegistry[_registryName] = totalVotesForNewRegistry[_registryName].sub(votesForNewRegistry[_registryName][msg.sender]);
        totalVotesForNewRegistry[_registryName] = totalVotesForNewRegistry[_registryName].add(stake[msg.sender]);
        votesForNewRegistry[_registryName][msg.sender] = stake[msg.sender];
        if (totalVotesForNewRegistry[_registryName] >= token.totalSupply() / 10) {
            registryName[_registryName] = true;
            registryList.push(_registryName);
            emit NewRegistry(_registryName);
        }
    }

    function cancelVoteForNewRegistry()
    private
    {
        string[] memory namesForRegistryNames = haveVotesForNewRegistry[msg.sender];
        for (uint256 v = 0; v < namesForRegistryNames.length; v++) {
            if (!registryName[namesForRegistryNames[v]]) {
                totalVotesForNewRegistry[namesForRegistryNames[v]] = totalVotesForNewRegistry[namesForRegistryNames[v]].sub(votesForNewRegistry[namesForRegistryNames[v]][msg.sender]);
                votesForNewRegistry[namesForRegistryNames[v]][msg.sender] = 0;
            }
        }
    }

    function vote(string _registryName, address _candidate)
    registryExist(_registryName)
    public
    {
        checkAndUpdateEpoch();
        address oldCandidate = candidateForVoter[_registryName][voteForEpoch][msg.sender];
        totalTokensForCandidate[_registryName][voteForEpoch][oldCandidate] = totalTokensForCandidate[_registryName][voteForEpoch][oldCandidate].sub(amountTokenForCandidateFromVoter[_registryName][voteForEpoch][msg.sender]);
        totalTokensForCandidate[_registryName][voteForEpoch][_candidate] = totalTokensForCandidate[_registryName][voteForEpoch][_candidate].add(stake[msg.sender]);
        amountTokenForCandidateFromVoter[_registryName][voteForEpoch][msg.sender] = stake[msg.sender];
        candidateForVoter[_registryName][voteForEpoch][msg.sender] = _candidate;
    }

    function voteService(uint256 _amount)
    public
    {
        checkAndUpdateEpoch();
        require(token.lockupExpired() < now);
        if (stakeLockup[msg.sender] > 0) {
            stakeLockup[msg.sender] = 0;
            stake[msg.sender] = 0;
        }
        stake[msg.sender] = stake[msg.sender].add(_amount);
        token.transferFrom(msg.sender, address(this), _amount);
    }

    function voteServiceLockup(uint256 _amount)
    public
    {
        checkAndUpdateEpoch();
        require(token.lockupExpired() > now);
        stake[msg.sender] = stake[msg.sender].add(_amount);
        if (stake[msg.sender] > token.balanceOf(msg.sender)) {
            stake[msg.sender] = token.balanceOf(msg.sender);
        }
        stakeLockup[msg.sender] = stake[msg.sender];
    }

    function withdraw()
    public
    {
        checkAndUpdateEpoch();
        require(stake[msg.sender] > 0);
        if (stakeLockup[msg.sender] == 0) {
            token.transfer(msg.sender, stake[msg.sender]);
        }
        stake[msg.sender] = 0;
        stakeLockup[msg.sender] = 0;
    }

    function getTotalTokensVotedForCandidate(
        string _registryName,
        uint16 _epoch,
        address _candidate)
    view
    public
    returns (uint256)
    {
        return totalTokensForCandidate[_registryName][_epoch][_candidate];
    }

    function isRegistryExist(string _name)
    view
    public
    returns (bool)
    {
        return registryName[_name];
    }

    function getTotalVotesForNewRegistry(string _name)
    view
    public
    returns (uint256)
    {
        return totalVotesForNewRegistry[_name];
    }

    /**
    * @dev Check and change number of current epoch
    */
    function checkAndUpdateEpoch()
    public
    {
        uint256 epochFinishTime = (epochZero + (epochTimeLimit.mul(currentEpoch + 1)));
        if (epochFinishTime < now) {
            currentEpoch = uint16((now.sub(epochZero)).div(epochTimeLimit));
            voteForEpoch = currentEpoch + 1;
            emit NewEpoch(currentEpoch);
        }
    }

}
