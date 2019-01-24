var GEOToken = artifacts.require("./GEOToken.sol");
var Voting = artifacts.require("./Voting.sol");
const assertRevert = require('./helpers/assertRevert').assertRevert;
const {increase, duration} = require('./helpers/time');

contract('Voting', accounts => {

    let geo, voting;
    const owner = accounts[0];
    const user1 = accounts[1];
    const user2 = accounts[2];
    const bigHolder = accounts[3];
    const bigHolderAllowTransfer = accounts[4];
    const lowBalanceUser = accounts[5];
    const userEmptyBalance = accounts[8];
    const candidatesList = [owner, user1];
    const amountForCandidatesList = [4000, 6000];

    before('setup', async () => {
        geo = await GEOToken.new({from: owner});
        voting = await Voting.new(geo.address, {from: owner});
        await geo.allowTransferInLockupPeriod(voting.address, {from: owner});

        console.log("\tgeo address", geo.address);
        console.log("\tvoting address", voting.address);
        await geo.transfer(user1, 1012345678, {from: owner});
        await geo.transfer(user2, 1012345678, {from: owner});
        await geo.transfer(lowBalanceUser, 100, {from: owner});
        await geo.transfer(bigHolder, (await geo.totalSupply()).toNumber() / 10 + 12345, {from: owner});
        await geo.transfer(bigHolderAllowTransfer, (await geo.totalSupply()).toNumber() / 10 + 12345, {from: owner});
        await geo.allowTransferInLockupPeriod(bigHolderAllowTransfer, {from: owner});
    });

    describe('Lockup period', () => {

        it('Vote for new registry, create registry', async () => {
            const name = "new registry";
            await assertRevert(voting.voteServiceForNewRegistry(name, {from: user1}));
            await voting.voteServiceLockupForNewRegistry(name, {from: user1});
            assert.equal(await voting.isRegistryExist(name), true, "Expected exist registry");
        });

        it('Vote for new registry, create registry, voter can transfer', async () => {
            const name = "registry1234";
            const howMany = await geo.totalSupply() / 10;
            await geo.approve(voting.address, howMany, {from: bigHolderAllowTransfer});
            await voting.makeDeposit(howMany, {from: bigHolderAllowTransfer});
            await voting.voteServiceForNewRegistry(name, {from: bigHolderAllowTransfer});
            assert.equal(await voting.isRegistryExist(name), true, "Can't create new registry");
        });

        it('Vote for registry, but exist registry', async () => {
            const name = "hub";//exist registry
            await assertRevert(voting.voteServiceLockupForNewRegistry(name, {from: user1}));
        });

        it('Vote without tokens', async () => {
            const name = "hub";
            await assertRevert(voting.voteServiceLockup(name, candidatesList, amountForCandidatesList, {from: userEmptyBalance}));
        });

        it('Vote for candidate, change vote', async () => {
            const name = "hub";
            const voter = user2;
            await voting.voteServiceLockup(name, candidatesList, amountForCandidatesList, {from: voter});
            await voting.voteServiceLockup(name, [user1], [10000], {from: voter});
        });
    });
});