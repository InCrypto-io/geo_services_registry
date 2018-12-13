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
            await assertRevert(gsr.voteForNewRegistry("new registry", {from: user1}));
            
            await gsr.voteServiceLockup(123123, {from: user1});
        });
    });

});