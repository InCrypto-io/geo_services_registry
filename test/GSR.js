var GEOToken = artifacts.require("./GEOToken.sol");
var GeoServiceRegistry = artifacts.require("./GeoServiceRegistry.sol");
const assertRevert = require('./helpers/assertRevert').assertRevert;
const {increase, duration} = require('./helpers/time');
const {sortBy} = require('lodash');

contract('GeoServiceRegistry', accounts => {

    let geo, gsr;
    const owner = accounts[0];
    const user1 = accounts[1];
    const user2 = accounts[2];
    const userEmptyBalance = accounts[8];
    const candidatesList = [owner, user1];
    const amountForCandidatesList = [15155, 551514];

    before('setup', async () => {
        geo = await GEOToken.new({from: owner});
        gsr = await GeoServiceRegistry.new(geo.address, {from: owner});

        console.log("\tgsr address", gsr.address);

        await geo.transfer(user1, 1012345678, {from: owner});
        await geo.transfer(user2, 1012345678, {from: owner});
    });

    describe('Lockup period', () => {

        it('Vote for new registry, small stake', async () => {
            const name = "new registry";
            const howMany = 123123;
            await assertRevert(gsr.voteServiceForNewRegistry(name, howMany, {from: user1}));
            // await gsr.voteServiceLockupForNewRegistry(name, howMany, {from: user1});
            // assert.equal(await gsr.isRegistryExist(name), false, "Unexpected registry");
            // assert.equal(await gsr.getTotalVotesForNewRegistry(name), howMany, "Unexpected votes for registry");
        });

        return;

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

        it('Vote without tokens', async () => {
            const name = "new registry";
            await assertRevert(gsr.voteServiceLockup(name, candidatesList, amountForCandidatesList, {from: userEmptyBalance}));
        });

        it('Vote for candidate, cancel vote, withdraw when have vote', async () => {
            const name = "registry0";
            const voter = user2;
            const candidate = user2;
            const currentEpoch = await gsr.currentEpoch();
            await gsr.vote(name, candidate, {from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                (await gsr.deposit(voter)).toNumber(),
                "Unexpected token count for candidate, after first vote");
            await gsr.cancelVote(name, {from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                0, "Unexpected token count for candidate, after cancel vote");
            await gsr.vote(name, candidate, {from: voter});
            await gsr.withdraw({from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                0, "Unexpected token count for candidate, after withdraw");
        });

        it('Epoch switch', async () => {
            await increase(duration.weeks(1));
            await gsr.checkEpoch();
            const currentEpoch = (await gsr.currentEpoch()).toNumber();
            await increase(duration.weeks(5));
            await gsr.checkEpoch();
            assert.equal((await gsr.currentEpoch()).toNumber(), currentEpoch + 5, "Unexpected current epoch");
        });
    });

    return;

    describe('After lockup period', () => {

        it("Switch to the period after the lock", async () => {
            await increase(duration.years(1));
            await gsr.checkEpoch();
            assert.isAbove((await gsr.currentEpoch()).toNumber(), 365 / 7, "Unexpected current epoch");
        });

        it("Make escrow and release", async () => {
            await gsr.checkEpoch();
            const howMany = 123123;
            await geo.approve(gsr.address, howMany, {from: user1});
            await gsr.voteService(howMany, {from: user1});
            assert.equal(await gsr.deposit(user1), howMany, "Unexpected escrow");
            await geo.approve(gsr.address, howMany, {from: user1});
            await gsr.voteService(howMany, {from: user1});
            assert.equal(await gsr.deposit(user1), howMany * 2, "Unexpected escrow");
            await geo.approve(gsr.address, howMany, {from: user1});
            await gsr.withdraw({from: user1});
            assert.equal(await gsr.deposit(user1), 0, "Unexpected escrow");
        });

        it('Test make escrow, lockup method', async () => {
            const howMany = 123123;
            await assertRevert(gsr.voteServiceLockup(howMany, {from: user1}));
        });

        it('Vote for new registry, small stake', async () => {
            const name = "new registry";
            await assertRevert(gsr.voteForNewRegistry("new registry", {from: user1}));
            const howMany = 123123;
            await geo.approve(gsr.address, howMany, {from: user1});
            await gsr.voteService(howMany, {from: user1});
            await gsr.voteForNewRegistry(name, {from: user1});
            assert.equal(await gsr.isRegistryExist(name), false, "Unexpected registry");
            assert.equal(await gsr.getTotalVotesForNewRegistry(name), howMany, "Unexpected votes for registry");
        });

        it('Withdraw, cancel vote for new registry', async () => {
            const name = "new registry";
            await gsr.withdraw({from: user1});
            assert.equal(await gsr.getTotalVotesForNewRegistry(name), 0, "Unexpected votes for registry");
        });

        it('Vote for candidate, cancel vote, withdraw when have vote', async () => {
            const name = "registry0";
            const voter = user2;
            const candidate = user2;
            const currentEpoch = await gsr.currentEpoch();
            const howMany = 123123;
            await geo.approve(gsr.address, howMany, {from: voter});
            await gsr.voteService(howMany, {from: voter});
            await gsr.vote(name, candidate, {from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                (await gsr.deposit(voter)).toNumber(),
                "Unexpected token count for candidate, after first vote");
            await gsr.cancelVote(name, {from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                0, "Unexpected token count for candidate, after cancel vote");
            await gsr.vote(name, candidate, {from: voter});
            await gsr.withdraw({from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, currentEpoch, candidate)).toNumber(),
                0, "Unexpected token count for candidate, after withdraw");
        });
    });
});