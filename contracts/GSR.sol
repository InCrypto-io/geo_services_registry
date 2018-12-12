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
    // (keccak256(registry name)) => (valid registry)
    mapping(bytes32 => bool) public registryName;
    // (keccak256(registry name)) => (amount votes for registry)
    mapping(bytes32 => uint256) public votesForRegistryName;

    uint16 public currentEpoch;
    uint256 private epochTimeLimit;
    uint256 private epochTime;

    modifier registryExist(string _name)
    {
        require(registryName[keccak256(_name)]);
        _;
    }

    constructor() public {
        epochTimeLimit = 7 days;
        currentEpoch = 0;
        restartEpochTime();
    }

    function voteForRegistry(string _name)
    public
    {
        require(registryName[keccak256(_name)] == false);
        votesForRegistryName[keccak256(_name)] = votesForRegistryName[keccak256(_name)] + stake[msg.sender];
        if (votesForRegistryName[keccak256(_name)] >= geo.totalSupply() / 10) {
            registryName[keccak256(_name)] = true;
            delete votesForRegistryName[keccak256(_name)];
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
