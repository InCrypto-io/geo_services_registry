var GEOToken = artifacts.require("./GEOToken.sol");
var Voting = artifacts.require("./Voting.sol");

module.exports = async function (deployer) {
    return deployer
        .then(_ => GEOToken.deployed())
        .then(async (token) => {
            await deployer.deploy(Voting, token.address);
        })
        .then(_ => Voting.deployed())
        .then(voting => {
            console.log("Voting address", voting.address)
        })
        .catch(console.error);
};
