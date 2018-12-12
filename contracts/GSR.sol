pragma solidity ^0.4.24;

import "./Ownable.sol";
import "./GEO.sol";
import "../math/SafeMath8.sol";
import "../math/SafeMath.sol";
import "../math/SafeMath16.sol";

contract GSR is Ownable {
    using SafeMath8 for uint8;
    using SafeMath16 for uint16;
    using SafeMath for uint256;

    GEO public geo;

    // (registry name) => (epoch) => (address) => (vote token amount)
    mapping (string => mapping(uint16 => mapping(address => uint256))) private registry;
    mapping (address => uint256) public stake;

    uint16 public currentEpoch;


    constructor() public {
        epochTimeLimit = 7 days;
        currentEpoch = 0;
        restartEpochTime();
    }


    function _addRegistry(string _name)
    private
    {

    }

    function voteForRegistry(sting name)
    public
    {

    }

    function vote(string _registryName)
    public
    {

    }

    function cancelVote(string _registryName)
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

    function withdraw()
    public
    {

    }

    /**
    * @dev Check and change number of current epoch
    */
    function checkEpoch()
    private
    returns(uint16)
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
    returns(uint16)
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
