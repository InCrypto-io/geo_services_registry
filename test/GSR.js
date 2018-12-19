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
    const bigHolder = accounts[3];
    const bigHolderAllowTransfer = accounts[4];
    const userEmptyBalance = accounts[8];
    const candidatesList = [owner, user1];
    const amountForCandidatesList = [15155, 551514];

    before('setup', async () => {
        geo = await GEOToken.new({from: owner});
        gsr = await GeoServiceRegistry.new(geo.address, {from: owner});
        await geo.allowTransferInLockupPeriod(gsr.address, {from: owner});

        console.log("\tgeo address", geo.address);
        console.log("\tgsr address", gsr.address);
        await geo.transfer(user1, 1012345678, {from: owner});
        await geo.transfer(user2, 1012345678, {from: owner});
        await geo.transfer(bigHolder, (await geo.totalSupply()) / 10 + 12345, {from: owner});
        await geo.transfer(bigHolderAllowTransfer, (await geo.totalSupply()) / 10 + 12345, {from: owner});
        await geo.allowTransferInLockupPeriod(bigHolderAllowTransfer, {from: owner});
    });

    describe('Lockup period', () => {

        it('Vote for new registry, small stake', async () => {
            const name = "new registry";
            const howMany = 123123;
            await assertRevert(gsr.voteServiceForNewRegistry(name, howMany, {from: user1}));
            await gsr.voteServiceLockupForNewRegistry(name, howMany, {from: user1});
            assert.equal(await gsr.isRegistryExist(name), false, "Unexpected registry");
            assert.equal(await gsr.getTotalVotesForNewRegistry(name), howMany, "Unexpected votes for registry");
        });

        it('Vote for new registry, create registry', async () => {
            const name = "registry0";
            const howMany = await geo.totalSupply() / 10;
            await assertRevert(gsr.voteServiceForNewRegistry(name, howMany, {from: bigHolder}));
            await gsr.voteServiceLockupForNewRegistry(name, howMany, {from: bigHolder});
            assert.equal(await gsr.isRegistryExist(name), true, "Can't create new registry");
        });

        it('Vote for new registry, create registry, voter can transfer', async () => {
            const name = "registry123";
            const howMany = await geo.totalSupply() / 10;
            await assertRevert(gsr.voteServiceLockupForNewRegistry(name, howMany, {from: bigHolderAllowTransfer}));
            await geo.approve(gsr.address, howMany, {from: bigHolderAllowTransfer});
            await gsr.voteServiceForNewRegistry(name, howMany, {from: bigHolderAllowTransfer});
            assert.equal(await gsr.isRegistryExist(name), true, "Can't create new registry");
            await assertRevert(gsr.withdraw({from: bigHolderAllowTransfer}));
            assert.equal((await gsr.deposit(bigHolderAllowTransfer)).toNumber(), howMany, "Unexpected deposit size");
            await increase(duration.weeks(2));
            await gsr.withdraw({from: bigHolderAllowTransfer});
            assert.equal((await gsr.deposit(bigHolderAllowTransfer)).toNumber(), 0, "Unexpected deposit size");
        });

        it('Vote without tokens', async () => {
            const name = "new registry";
            await assertRevert(gsr.voteServiceLockup(name, candidatesList, amountForCandidatesList, {from: userEmptyBalance}));
        });

        it('Vote for candidate, change vote', async () => {
            const name = "registry0";
            const voter = user2;
            await gsr.checkAndUpdateEpoch({from: voter});
            const nextEpoch = (await gsr.currentEpoch()).toNumber() + 1;
            await gsr.voteServiceLockup(name, candidatesList, amountForCandidatesList, {from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, nextEpoch, candidatesList[0])).toNumber(),
                amountForCandidatesList[0],
                "Unexpected token count for candidate, after first vote");
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, nextEpoch, candidatesList[1])).toNumber(),
                amountForCandidatesList[1],
                "Unexpected token count for candidate, after first vote");
            await gsr.voteServiceLockup(name, [], [], {from: voter});
            assert.equal((await gsr.getTotalTokensVotedForCandidate(name, nextEpoch, candidatesList[0])).toNumber(),
                0, "Unexpected token count for candidate, after change vote");
        });

        it('Epoch switch', async () => {
            await increase(duration.weeks(1));
            await gsr.checkAndUpdateEpoch();
            const currentEpoch = (await gsr.currentEpoch()).toNumber();
            await increase(duration.weeks(5));
            await gsr.checkAndUpdateEpoch();
            assert.equal((await gsr.currentEpoch()).toNumber(), currentEpoch + 5, "Unexpected current epoch");
        });
    });

    describe('After lockup period', () => {

        it("Switch to the period after the lock", async () => {
            await increase(duration.years(1));
            await gsr.checkAndUpdateEpoch();
            assert.isAbove((await gsr.currentEpoch()).toNumber(), 365 / 7, "Unexpected current epoch");
        });

        it('Vote by lockup method', async () => {
            const howMany = 123123;
            await assertRevert(gsr.voteServiceLockup(howMany, candidatesList, amountForCandidatesList, {from: user1}));
        });

        it('Vote for new registry, small stake', async () => {
            const name = "new registry 2";
            const howMany = 123123;
            await assertRevert(gsr.voteServiceLockupForNewRegistry(name, howMany, {from: user1}));
            await geo.approve(gsr.address, howMany, {from: user1});
            await gsr.voteServiceForNewRegistry(name, howMany, {from: user1});
            assert.equal(await gsr.isRegistryExist(name), false, "Unexpected registry");
            assert.equal(await gsr.getTotalVotesForNewRegistry(name), howMany, "Unexpected votes for registry");
        });

        return;
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