var GEO = artifacts.require("./GEO.sol");
var GSR = artifacts.require("./GSR.sol");
const assertRevert = require('./helpers/assertRevert').assertRevert;

contract('GSR', accounts => {

    let geo, gsr;
    const owner = accounts[0];
    const user1 = accounts[1];

    before('setup', async () => {
        geo = await GEO.new({from: owner});
        gsr = await GSR.new(geo.address, {from: owner});

        console.log("gsr address",gsr.address);

        geo.transfer(user1, 1012345678, {from: owner});
    });

    describe('Lockup period', () => {
        it('Make escrow and release', async () => {
            const howMany = 123123;
            await gsr.voteServiceLockup(howMany, {from: user1});
            assert.equal(await gsr.stake(user1), howMany, "Unexpected escrow");
            assert.equal(await gsr.stakeLockup(user1), howMany, "Unexpected escrow");
            await gsr.voteServiceLockup(howMany, {from: user1});
            assert.equal(await gsr.stake(user1), howMany*2, "Unexpected escrow");
            assert.equal(await gsr.stakeLockup(user1), howMany*2, "Unexpected escrow");
            await gsr.withdraw({from: user1});
            assert.equal(await gsr.stake(user1), 0, "Unexpected escrow");
            assert.equal(await gsr.stakeLockup(user1), 0, "Unexpected escrow");
        });

        it('Vote for new registry, small stake', async () => {
            const name = "new registry";
            await assertRevert(gsr.voteForNewRegistry("new registry", {from: user1}));
            const howMany = 123123;
            await gsr.voteServiceLockup(howMany, {from: user1});
            await gsr.voteForNewRegistry(name, {from: user1});
            assert.equal(await gsr.isRegistryExist(name),false,"Unexpected registry");
            assert.equal(await gsr.getTotalVotesForNewRegistry(name),howMany,"Unexpected votes for registry");
        });

        it('Withdraw, cancel vote for new registry', async () => {
            const name = "new registry";
            await gsr.withdraw({from: user1});
            assert.equal(await gsr.getTotalVotesForNewRegistry(name),0,"Unexpected votes for registry");
        });

        it('Vote for new registry, create registry', async () => {
            const name = "registry0";
            const who = owner;
            await assertRevert(gsr.voteForNewRegistry("new registry", {from: who}));
            const howMany = await geo.totalSupply() / 10;
            await gsr.voteServiceLockup(howMany, {from: who});
            await gsr.voteForNewRegistry(name, {from: who});
            assert.equal(await gsr.isRegistryExist(name),true,"Can't create new registry");
        });
    });

});