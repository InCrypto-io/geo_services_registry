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

    mapping(address => uint256) public deposit;

    // (keccak256(registry name)) => (epoch) => (candidate address) => (total votes amount)
    mapping(string => mapping(uint16 => mapping(address => uint256))) private totalTokensForCandidate;
    // (keccak256(registry name)) => (epoch) => (voter address) => (vote amount)
    mapping(string => mapping(uint16 => mapping(address => uint256))) private amountTokenForCandidateFromVoter;
    // (keccak256(registry name)) => (epoch) => (voter address) => (candidate address)
    mapping(string => mapping(uint16 => mapping(address => address))) private candidateForVoter;

    mapping(string => bool) private registryName;
    // (keccak256(registry name)) => (epoch) => (total votes amount)
    mapping(string => mapping(uint16 => uint256)) private totalVotesForNewRegistry;
    // (keccak256(registry name)) => (epoch) => (voter address) => (amount vote from address)
    mapping(string => mapping(uint16 => mapping(address => uint256))) private votesForNewRegistry;

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

    function _voteForNewRegistry(string _registryName)
    private
    {
        checkAndUpdateEpoch();
        require(registryName[_registryName] == false);
        totalVotesForNewRegistry[_registryName][voteForEpoch] = totalVotesForNewRegistry[_registryName][voteForEpoch].sub(votesForNewRegistry[_registryName][voteForEpoch][msg.sender]);
        totalVotesForNewRegistry[_registryName][voteForEpoch] = totalVotesForNewRegistry[_registryName][voteForEpoch].add(deposit[msg.sender]);
        votesForNewRegistry[_registryName][voteForEpoch][msg.sender] = deposit[msg.sender];
        if (totalVotesForNewRegistry[_registryName][voteForEpoch] >= token.totalSupply() / 10) {
            registryName[_registryName] = true;
            emit NewRegistry(_registryName);
        }
    }

    function _vote(string _registryName, address _candidate)
    registryExist(_registryName)
    private
    {
        checkAndUpdateEpoch();
        address oldCandidate = candidateForVoter[_registryName][voteForEpoch][msg.sender];
        totalTokensForCandidate[_registryName][voteForEpoch][oldCandidate] = totalTokensForCandidate[_registryName][voteForEpoch][oldCandidate].sub(amountTokenForCandidateFromVoter[_registryName][voteForEpoch][msg.sender]);
        totalTokensForCandidate[_registryName][voteForEpoch][_candidate] = totalTokensForCandidate[_registryName][voteForEpoch][_candidate].add(deposit[msg.sender]);
        amountTokenForCandidateFromVoter[_registryName][voteForEpoch][msg.sender] = deposit[msg.sender];
        candidateForVoter[_registryName][voteForEpoch][msg.sender] = _candidate;
    }

    function voteService(
        uint256 _amount,
        string _registryName,
        address _candidate)
    public
    {
        checkAndUpdateEpoch();
        require(token.lockupExpired() < now);
        deposit[msg.sender] = deposit[msg.sender].add(_amount);
        token.transferFrom(msg.sender, address(this), _amount);
    }

    function voteServiceLockup(uint256 _amount)
    public
    {
        checkAndUpdateEpoch();
        require(token.lockupExpired() > now);
    }

    function withdraw()
    public
    {
        checkAndUpdateEpoch();
        require(deposit[msg.sender] > 0);
        token.transfer(msg.sender, deposit[msg.sender]);
        deposit[msg.sender] = 0;
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

    function isRegistryExist(string _registryName)
    view
    public
    returns (bool)
    {
        return registryName[_registryName];
    }

    function getTotalVotesForNewRegistry(string _registryName)
    view
    public
    returns (uint256)
    {
        return totalVotesForNewRegistry[_registryName][voteForEpoch];
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
