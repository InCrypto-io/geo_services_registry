var GEO = artifacts.require("./GEO.sol");
var GSR = artifacts.require("./GSR.sol");

module.exports = async function(deployer, accounts) {
    return deployer
        .then(_ => deployer.deploy(GSR, accounts[0]))
        .then(_ => GSR.deployed())
        .then(gsr => {
            deployer.deploy(GEO, gsr)
        })
        .catch(console.error);
};
