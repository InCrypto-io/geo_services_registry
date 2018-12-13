
const campaignFields = Object.freeze({ timeSlots:0, status:1, expirationTime:2,
	balance:3, couponReleased:4, couponRedeemed:5, couponConfirmed:6 });

getFromCampaign = (campaign, field) => {
	if (!campaignFields.hasOwnProperty(field))
	{
		throw Error('Invalid Campaign field: ' + field);
	}
	return campaign[campaignFields[field]];
}

doAndReturn = async (execFunc, responseFunc, execArgs, responseArgs) => {
    if( !(execArgs instanceof Array) || !(responseArgs instanceof Array) ) throw new Error('Arguments must be an array');
    
    await execFunc(...execArgs);

    const res = await responseFunc(...responseArgs);
    return res;
}


module.exports = {
    doAndReturn: doAndReturn,
	campaignState: Object.freeze({ uninitialized:0, created:1, active:2,
		paused:3, insufficient_funds:4, finished:5 }),
	getFromCampaign: getFromCampaign,

	testConfirmCouponVU: async (platform, campaign, user, confirmValue, currencyId, currencyRate) => {
		var m = await platform.getCustomerCoupons(user, campaign.id);
        const userCouponsBefore = (m[1])
            .map(element => element.toNumber());
        const campaignBefore = await platform.getCampaign(campaign.id);
        const campaignBalanceBefore = getFromCampaign(campaignBefore, 'balance')
        	.toNumber();
        const couponsRedeemedBefore = getFromCampaign(campaignBefore, 'couponRedeemed')
        	.toNumber();
        const couponsConfirmedBefore = getFromCampaign(campaignBefore, 'couponConfirmed')
        	.toNumber();
        const vendorDebenturesBefore = (await platform.getVendorDebentures(campaign.vendor))
        	.toNumber();
        const balanceOperatorBefore = (await platform.getBalanceOperator())
        	.toNumber();
        const res = await doAndReturn(platform.confirmCouponVU,
            platform.getCampaign,
            [user, campaign.id, currencyId, confirmValue, {from: campaign.vendor}],
            [campaign.id]);

        const userCouponId = userCouponsBefore.indexOf(1);
        assert.equal(2,
            (await platform.getCustomerCoupons(user, campaign.id))[1][userCouponId].toNumber(),
            'User coupon hasn`t been marked as used');
        assert.equal(getFromCampaign(res, 'couponRedeemed').toNumber(),
            couponsRedeemedBefore - 1,
            'Coupons redeemed number is wrong');
        assert.equal(getFromCampaign(res, 'couponConfirmed').toNumber(),
            couponsConfirmedBefore + 1,
            'Coupons confirmed number is wrong');

        //value that will be withdrawn from campaign balance
        const expectedValue = (campaign.percFee * currencyRate * confirmValue) / 100;
        const expectedCampaignBalance = (expectedValue > campaignBalanceBefore) ?
            0 : campaignBalanceBefore - expectedValue;
        const expectedCampaignBalanceDiff = campaignBalanceBefore - expectedCampaignBalance;
        const expectedDebenturesDiff = expectedValue - expectedCampaignBalanceDiff;

        const campaignBalanceAfter = getFromCampaign(res, 'balance').toNumber();
        const vendorDebenturesAfter = (await platform.getVendorDebentures(campaign.vendor))
        	.toNumber();
        const balanceOperatorAfter = (await platform.getBalanceOperator())
        	.toNumber();
        const campaignBalanceDiff = campaignBalanceBefore - campaignBalanceAfter;
        const vendorDebenturesDiff = vendorDebenturesAfter - vendorDebenturesBefore;
        const operatorBalanceDiff = balanceOperatorAfter - balanceOperatorBefore;
        assert.equal(expectedCampaignBalanceDiff, campaignBalanceDiff,
            'Campaign balance is wrong');
        assert.equal(expectedDebenturesDiff, vendorDebenturesDiff,
            'Vendor debentures number is wrong');
        assert.equal(operatorBalanceDiff,
            campaignBalanceDiff,
        	'Operator balance changes must match campaign balance changes');
	},

	testConfirmCouponVK: async (platform, campaign, user, currencyId, currencyRate) => {
        var m = await platform.getCustomerCoupons(user, campaign.id);
		const userCouponsBefore = (m[1])
            .map(element => element.toNumber());
        const campaignBefore = await platform.getCampaign(campaign.id);
        const campaignBalanceBefore = getFromCampaign(campaignBefore, 'balance')
        	.toNumber();
        const couponsRedeemedBefore = getFromCampaign(campaignBefore, 'couponRedeemed')
        	.toNumber();
        const couponsConfirmedBefore = getFromCampaign(campaignBefore, 'couponConfirmed')
        	.toNumber();
        const vendorDebenturesBefore = (await platform.getVendorDebentures(campaign.vendor))
        	.toNumber();
        const balanceOperatorBefore = (await platform.getBalanceOperator())
        	.toNumber();
        const res = await doAndReturn(platform.confirmCouponVK,
            platform.getCampaign,
            [user, campaign.id, currencyId, {from:campaign.vendor}],
            [campaign.id]);

        const userCouponId = userCouponsBefore.indexOf(1);
        assert.equal(2,
            (await platform.getCustomerCoupons(user, campaign.id))[1][userCouponId].toNumber(),
            'User coupon hasn`t been marked as used');
        assert.equal(getFromCampaign(res, 'couponRedeemed').toNumber(),
            couponsRedeemedBefore - 1,
            'Coupons redeemed number is wrong');
        assert.equal(getFromCampaign(res, 'couponConfirmed').toNumber(),
            couponsConfirmedBefore + 1,
            'Coupons confirmed number is wrong');

        //value that will be withdrawn from campaign balance
        const expectedValue = campaign.fixedFee * currencyRate;
        const expectedCampaignBalance = (expectedValue > campaignBalanceBefore) ?
            0 : campaignBalanceBefore - expectedValue;
        const expectedCampaignBalanceDiff = campaignBalanceBefore - expectedCampaignBalance;
        const expectedDebenturesDiff = expectedValue - expectedCampaignBalanceDiff;

        const campaignBalanceAfter = getFromCampaign(res, 'balance').toNumber();
        const vendorDebenturesAfter = (await platform.getVendorDebentures(campaign.vendor))
        	.toNumber();
        const balanceOperatorAfter = (await platform.getBalanceOperator())
        	.toNumber();
        const campaignBalanceDiff = campaignBalanceBefore - campaignBalanceAfter;
        const vendorDebenturesDiff = vendorDebenturesAfter - vendorDebenturesBefore;
        const operatorBalanceDiff = balanceOperatorAfter - balanceOperatorBefore;

        assert.equal(expectedCampaignBalanceDiff, campaignBalanceDiff,
            'Campaign balance is wrong');
        assert.equal(expectedDebenturesDiff, vendorDebenturesDiff,
            'Vendor debentures number is wrong');
        assert.equal(operatorBalanceDiff,
            campaignBalanceDiff,
            'Operator balance changes must match campaign balance changes');
	},

    sleep: (ms) => {
    	return new Promise(resolve => setTimeout(resolve, ms));
	}
}