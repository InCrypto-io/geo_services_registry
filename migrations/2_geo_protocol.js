var GEO = artifacts.require("./GEOToken.sol");
var GSR = artifacts.require("./GSR.sol");

module.exports = async function (deployer) {
    return deployer
        .then(_ => deployer.deploy(GEO))
        .then(_ => GEO.deployed())
        .then(geo => {
            deployer.deploy(GSR, geo.address);
        })
        .catch(console.error);
};
