const GSR = artifacts.require('GSR');

module.exports = (deployer, network, accounts) => {

    deployer
        .then(_ => deployer.deploy(GSR))
        .catch(console.error);
};
