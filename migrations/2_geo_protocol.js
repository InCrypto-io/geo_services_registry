var GEOToken = artifacts.require("./GEOToken.sol");
var Voting = artifacts.require("./Voting.sol");

module.exports = async function (deployer) {
    return deployer
        .then(_ => deployer.deploy(GEOToken))
        .then(_ => GEOToken.deployed())
        .then(token => {
            deployer.deploy(Voting, token.address);
        })
        .catch(console.error);
};
