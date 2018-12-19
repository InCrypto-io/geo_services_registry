var GEOToken = artifacts.require("./GEOToken.sol");
var GeoServiceRegistry = artifacts.require("./GeoServiceRegistry.sol");

module.exports = async function (deployer) {
    return deployer
        .then(_ => deployer.deploy(GEOToken))
        .then(_ => GEOToken.deployed())
        .then(geo => {
            deployer.deploy(GeoServiceRegistry, geo.address);
        })
        .catch(console.error);
};
