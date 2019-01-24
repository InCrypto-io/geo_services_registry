var GEOToken = artifacts.require("./GEOToken.sol");

module.exports = async function (deployer) {
    return deployer
        .then(_ => deployer.deploy(GEOToken))
        .catch(console.error);
};
