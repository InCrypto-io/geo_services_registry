var GEO = artifacts.require("./GEO.sol");
var GSR = artifacts.require("./GSR.sol");
const assertRevert = require('./helpers/assertRevert').assertRevert;
const {increase,duration} = require('./helpers/time');

contract('GSR', accounts => {

    let geo, gsr;
    const owner = accounts[0];
    const user1 = accounts[1];
    const user2 = accounts[2];

    before('setup', async () => {
        geo = await GEO.new({from: owner});
        gsr = await GSR.new(geo.address, {from: owner});

        console.log("gsr address", gsr.address);

        geo.transfer(user1, 1012345678, {from: owner});
        geo.transfer(user2, 1012345678, {from: owner});
        gsr.voteServiceLockup(1012345678, {from: user2});
    });

    describe('Lockup period', () => {
        it('Make escrow and release', async () => {
            const howMany = 123123;
            await gsr.voteServiceLockup(howMany, {from: user1});
            assert.equal(await gsr.stake(user1), howMany, "Unexpected escrow");
            assert.equal(await gsr.stakeLockup(user1), howMany, "Unexpected escrow");
            await gsr.voteServiceLockup(howMany, {from: user1});
            assert.equal(await gsr.stake(user1), howMany * 2, "Unexpected escrow");
            assert.equal(await gsr.stakeLockup(user1), howMany * 2, "Unexpected escrow");
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
            assert.equal(await gsr.isRegistryExist(name), false, "Unexpected registry");
            assert.equal(await gsr.getTotalVotesForNewRegistry(name), howMany, "Unexpected votes for registry");
        });

        it('Withdraw, cancel vote for new registry', async () => {
            const name = "new registry";
            await gsr.withdraw({from: user1});
            assert.equal(await gsr.getTotalVotesForNewRegistry(name), 0, "Unexpected votes for registry");
        });

        it('Vote for new registry, create registry', async () => {
            const name = "registry0";
            const who = owner;
            await assertRevert(gsr.voteForNewRegistry("new registry", {from: who}));
            const howMany = await geo.totalSupply() / 10;
            await gsr.voteServiceLockup(howMany, {from: who});
            await gsr.voteForNewRegistry(name, {from: who});
            assert.equal(await gsr.isRegistryExist(name), true, "Can't create new registry");
        });

        it('Vote for candidate, cancel vote, withdraw when have vote', async () => {
            const name = "registry0";
            const voter = user2;
            const candidate = user2;
            const currentEpoch = await gsr.currentEpoch();
            await gsr.vote(name, candidate, {from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                (await gsr.stake(voter)).toNumber(),
                "Unexpected token count for candidate, after first vote");
            await gsr.cancelVote(name,{from:voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                0, "Unexpected token count for candidate, after cancel vote");
            await gsr.vote(name, candidate, {from: voter});
            await gsr.withdraw({from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                0, "Unexpected token count for candidate, after withdraw");
        });

        it('Epoch switch', async () => {
            const currentEpoch = (await gsr.currentEpoch()).toNumber();
            await increase(duration.weeks(1));
            await gsr.checkEpoch();
            assert.equal((await gsr.currentEpoch()).toNumber(), currentEpoch+1, "Unexpected current epoch");
        });
    });

});