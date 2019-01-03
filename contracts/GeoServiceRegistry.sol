pragma solidity ^0.4.24;

import "./GEOToken.sol";
import "./math/SafeMath8.sol";
import "./math/SafeMath.sol";
import "./math/SafeMath16.sol";

contract GeoServiceRegistry {
    using SafeMath8 for uint8;
    using SafeMath16 for uint16;
    using SafeMath for uint256;

    // STORAGE //
    GEOToken private token;

    // The balance of the user in tokens, which is deposited on the contract
    mapping(address => uint256) public deposit;

    // (registry name) => (exist)
    mapping(string => bool) private existingRegistries;

    // STORAGE END //

    /* EVENTS
    */

    event VoteForNewRegistry(string _name, uint256 _amount);
    event NewRegistry(string _name);
    event Vote(string _name, address _candidate, uint256 _amount);
    event CancelVote(string _name, address _candidate, uint256 _amount);
    event Withdrawal(address _voter, uint256 _amountWithdraw);

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
        _voteForNewRegistry("observer");
        _voteForNewRegistry("provider");
        _voteForNewRegistry("hub");
    }

    /* FUNCTIONS
    */

    /**
    * @dev Vote for new registry.
    * After collect target count votes, create a registry.
    * @param _registryName Proposed registry name.
    */
    function _voteForNewRegistry(
        string _registryName)
    private
    {
        require(existingRegistries[_registryName] == false);
        existingRegistries[_registryName] = true;
        emit NewRegistry(_registryName);
    }

    /**
    * @dev Vote for candidate in registry.
    * Maximum candidates 20
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
        require(_candidates.length <= 20 && _candidates.length == _amounts.length);
        require(sumOfArray(_amounts) == 10000);
        for (uint256 n = 0; n < _candidates.length; n++) {
            emit Vote(_registryName, _candidates[n], _amounts[n]);
        }
    }

    /**
    * @dev Vote for candidate in registry.
    * Method for vote after lockup period.
    * Maximum candidates 10.
    * Sender must approve tokens for deposit to contract address.
    * @param _registryName Exist registry name.
    * @param _candidates List of candidates.
    * @param _amounts List of votes for corresponding candidates in tokens.
    */
    function voteService(
        string _registryName,
        address[] _candidates,
        uint256[] _amounts)
    public
    {
        require(deposit[msg.sender] >= _amount); // todo

        require(sumOfArray(_amounts) == 10000);
        _vote(_registryName, _candidates, _amounts);
    }


    /**
    * @dev Vote for candidate in registry.
    * Method for vote in lockup period.
    * Maximum candidates 10.
    * @param _registryName Exist registry name.
    * @param _candidates List of candidates.
    * @param _amounts List of votes for corresponding candidates in tokens.
    */
    function voteServiceLockup(
        string _registryName,
        address[] _candidates,
        uint256[] _amounts)
    public
    {
        require(!token.isLockupExpired(msg.sender));

        require(token.balanceOf(msg.sender) >= 0);  // todo

        _vote(_registryName, _candidates, _amounts);
    }

    /**
    * @dev Vote for new registry.
    * Method for vote after lockup period.
    * @param _registryName Proposed registry name.
    */
    function voteServiceForNewRegistry(
        string _registryName)
    public
    {
        require(deposit[msg.sender] > 0);

        require(deposit[msg.sender] >= _amount); // todo

        _voteForNewRegistry(_registryName);
    }


    /**
    * @dev Vote for new registry.
    * Method for vote in lockup period.
    * @param _registryName Proposed registry name.
    */
    function voteServiceLockupForNewRegistry(
        string _registryName)
    public
    {
        require(!token.isLockupExpired(msg.sender));

        require(token.balanceOf(msg.sender) >= 0);  // todo

        _voteForNewRegistry(_registryName);
    }

    /**
    * @dev Used after lockup period.
    * Sender must approve tokens for deposit to contract address.
    * Check size of deposit an increase if need.
    * @param _amount Target level of deposit.
    */
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

    /**
    * @dev Used in lockup period.
    * Compare balance of address corresponding sender with target value.
    * @param _amount Require minimum tokens in GEOToken.
    */
    function _checkSolvencyInLockupPeriod(
        uint256 _amount)
    view
    private
    {
        require(!token.isLockupExpired(msg.sender));
        require(token.balanceOf(msg.sender) >= _amount);
    }

    /**
    * @dev Transfer tokens back to deposit creator.
    * @param _amount Withdraw part or full deposit.
    */
    function withdraw(
        uint _amount)
    public
    {
        require(deposit[msg.sender] >= _amount);
        token.transfer(msg.sender, deposit[msg.sender]);
        deposit[msg.sender] = deposit[msg.sender].sub(_amount);
        emit Withdrawal(msg.sender, _amount);
    }

    /**
    * @dev Check for the existence of a register.
    * @param _registryName Exist registry name.
    * @return bool True if registry exist.
    */
    function isRegistryExist(
        string _registryName)
    view
    public
    returns (bool)
    {
        return existingRegistries[_registryName];
    }

    /**
    * @dev Calculate sum of input array.
    * @param _array Array of uint256.
    * @return uint256 Total sum.
    */
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
