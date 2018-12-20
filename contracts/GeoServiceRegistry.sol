pragma solidity ^0.4.24;

import "./GEOToken.sol";
import "./math/SafeMath8.sol";
import "./math/SafeMath.sol";
import "./math/SafeMath16.sol";

contract GeoServiceRegistry {
    using SafeMath8 for uint8;
    using SafeMath16 for uint16;
    using SafeMath for uint256;

    // STORAGE
    GEOToken private token;

    // The balance of the user in tokens, which is deposited on the contract
    mapping(address => uint256) public deposit;

    // The time after which the user will be able to withdraw their tokens.
    mapping(address => uint256) public withdrawalBlockingTime;

    // Total counting of votes for a candidate, broken down by epochs and registries
    // (registry name) => (epoch) => (candidate address) => (total votes amount)
    mapping(string => mapping(uint16 => mapping(address => uint256))) private totalVotesForCandidate;

    // List of candidates from voters, broken down by epochs and registries
    // (registry name) => (epoch) => (voter address) => (candidates addresses)
    mapping(string => mapping(uint16 => mapping(address => address[]))) private selectedCandidatesByVoter;

    // List of votes, broken down by epochs and and registries
    // (registry name) => (epoch) => (voter address) => (vote amounts)
    mapping(string => mapping(uint16 => mapping(address => uint256[]))) private votesForCandidatesChosenByVoters;

    // (registry name) => (exist)
    mapping(string => bool) private existingRegistries;

    // Proposed registries with corresponding votes broken down by epoch
    // (registry name) => (epoch) => (total votes amount)
    mapping(string => mapping(uint16 => uint256)) private totalVotesForNewRegistry;

    // Votes size for proposed registries broken down by epoch and voters
    // (registry name) => (epoch) => (voter address) => (amount vote from address)
    mapping(string => mapping(uint16 => mapping(address => uint256))) private votesForNewRegistry;

    uint16 public currentEpoch;

    // Voting doing in next epoch
    uint16 private voteForEpoch;

    uint256 private epochTimeLimit;

    // Time of start first epoch
    uint256 private epochZero;

    /* EVENTS
    */

    event NewEpoch(uint256 _number);
    event VoteForNewRegistry(string _name, uint256 _amou);
    event NewRegistry(string _name);
    event Vote(string _name, address _candidate, uint256 _amount);
    event CancelVote(string _name, address _candidate, uint256 _amount);

    /* MODIFIERS
    */

    /**
    * @dev Modifier to make a function callable only if registry exist.
    */
    modifier registryExist(
        string _name)
    {
        require(existingRegistries[_name]);
        _;
    }

    /* CONSTRUCTOR
    */

    constructor(
        address _geoAddress)
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

    /**
    * @dev Vote for new registry.
    * After collect target count votes, create a registry.
    * Votes going by epoch.
    * @param _registryName Proposed registry name.
    * @param _amount Size of vote in tokens.
    */
    function _voteForNewRegistry(
        string _registryName,
        uint256 _amount)
    private
    {
        checkAndUpdateEpoch();
        require(existingRegistries[_registryName] == false);
        totalVotesForNewRegistry[_registryName][voteForEpoch] = totalVotesForNewRegistry[_registryName][voteForEpoch].sub(votesForNewRegistry[_registryName][voteForEpoch][msg.sender]);
        totalVotesForNewRegistry[_registryName][voteForEpoch] = totalVotesForNewRegistry[_registryName][voteForEpoch].add(_amount);
        votesForNewRegistry[_registryName][voteForEpoch][msg.sender] = _amount;
        // For create a new registry, need collect 10% of total supply
        if (totalVotesForNewRegistry[_registryName][voteForEpoch] >= token.totalSupply() / 10) {
            existingRegistries[_registryName] = true;
            emit NewRegistry(_registryName);
        } else {
            emit VoteForNewRegistry(_registryName, _amount);
        }
    }

    /**
    * @dev Vote for candidate in registry.
    * Maximum candidates 10
    * Votes going by epoch.
    * @param _registryName Exist registry name.
    * @param _candidates List of candidates.
    * @param _amounts List of votes for corresponding candidates in tokens.
    */
    function _vote(
        string _registryName,
        address[] _candidates,
        uint256[] _amounts)
    registryExist(_registryName)
    private
    {
        require(_candidates.length < 10 && _candidates.length == _amounts.length);
        uint256 oldCandidatesCount = selectedCandidatesByVoter[_registryName][voteForEpoch][msg.sender].length;
        for (uint256 o = 0; o < oldCandidatesCount; o++) {
            address oldCandidate = selectedCandidatesByVoter[_registryName][voteForEpoch][msg.sender][o];
            uint256 amount = votesForCandidatesChosenByVoters[_registryName][voteForEpoch][msg.sender][o];
            totalVotesForCandidate[_registryName][voteForEpoch][oldCandidate] = totalVotesForCandidate[_registryName][voteForEpoch][oldCandidate].sub(amount);
            emit CancelVote(_registryName, oldCandidate, amount);
        }
        delete selectedCandidatesByVoter[_registryName][voteForEpoch][msg.sender];
        delete votesForCandidatesChosenByVoters[_registryName][voteForEpoch][msg.sender];
        uint256 candidatesCount = _candidates.length;
        for (uint256 n = 0; n < candidatesCount; n++) {
            address candidate = _candidates[n];
            totalVotesForCandidate[_registryName][voteForEpoch][candidate] = totalVotesForCandidate[_registryName][voteForEpoch][candidate].add(_amounts[n]);
            selectedCandidatesByVoter[_registryName][voteForEpoch][msg.sender].push(candidate);
            votesForCandidatesChosenByVoters[_registryName][voteForEpoch][msg.sender].push(_amounts[n]);
            emit Vote(_registryName, candidate, _amounts[n]);
        }
    }

    function voteService(
        string _registryName,
        address[] _candidates,
        uint256[] _amounts)
    public
    {
        checkAndUpdateEpoch();
        uint256 amount = sumOfArray(_amounts);
        _checkOrReplenishDeposit(amount);
        _vote(_registryName, _candidates, _amounts);
        _lockupWithdrawForNextEpoch();
    }

    function voteServiceLockup(
        string _registryName,
        address[] _candidates,
        uint256[] _amounts)
    public
    {
        checkAndUpdateEpoch();
        uint256 amount = sumOfArray(_amounts);
        _checkSolvencyInLockupPeriod(amount);
        _vote(_registryName, _candidates, _amounts);
    }

    function voteServiceForNewRegistry(
        string _registryName,
        uint256 _amount)
    public
    {
        checkAndUpdateEpoch();
        _checkOrReplenishDeposit(_amount);
        _voteForNewRegistry(_registryName, _amount);
        _lockupWithdrawForNextEpoch();
    }

    function voteServiceLockupForNewRegistry(
        string _registryName,
        uint256 _amount)
    public
    {
        checkAndUpdateEpoch();
        _checkSolvencyInLockupPeriod(_amount);
        _voteForNewRegistry(_registryName, _amount);
    }

    function _checkOrReplenishDeposit(
        uint256 _amount)
    private
    {
        require(token.isLockupExpired(msg.sender));
        if (deposit[msg.sender] < _amount) {
            uint256 additionAmount = _amount.sub(deposit[msg.sender]);
            deposit[msg.sender] = deposit[msg.sender].add(additionAmount);
            token.transferFrom(msg.sender, address(this), additionAmount);
        }
        require(deposit[msg.sender] >= _amount);
    }

    function _checkSolvencyInLockupPeriod(
        uint256 _amount)
    view
    private
    {
        require(!token.isLockupExpired(msg.sender));
        require(token.balanceOf(msg.sender) >= _amount);
    }

    function _lockupWithdrawForNextEpoch()
    private
    {
        withdrawalBlockingTime[msg.sender] = (epochZero + (epochTimeLimit.mul(voteForEpoch + 1)));
    }

    function withdraw()
    public
    {
        checkAndUpdateEpoch();
        require(withdrawalBlockingTime[msg.sender] < now);
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
        return totalVotesForCandidate[_registryName][_epoch][_candidate];
    }

    function isRegistryExist(
        string _registryName)
    view
    public
    returns (bool)
    {
        return existingRegistries[_registryName];
    }

    function getTotalVotesForNewRegistry(
        string _registryName)
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

    function sumOfArray(
        uint256[] _array)
    pure
    private
    returns (uint256)
    {
        uint256 amount = 0;
        for (uint256 n = 0; n < _array.length; n++) {
            amount = amount.add(_array[n]);
        }
        return amount;
    }

}
