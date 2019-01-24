var GSR = artifacts.require("GSR");

contract('GSR', function(accounts) {

    it("create, get, remove records", async () => {
        const gsr = await GSR.deployed();

        console.log("address",gsr.address);

        await gsr.createRecord("name",['0x00','0x00','0x00','0x00','0x03','0x31','0x32','0x33']);
        await gsr.createRecord("name",['0x00','0x00','0x00','0x00','0x03','0x31','0x2e','0x33']);
        await gsr.createRecord("name",['0x00','0x00','0x00','0x00','0x03','0x71','0x42','0x33']);
        await gsr.createRecord("name1",['0x00','0x00','0x00','0x00','0x03','0x71','0x42','0x33']);
        await gsr.createRecord("name",['0x01','0xff','0xff','0xff','0xaa']);
        await gsr.createRecord("name",['0x01','0xff','0xbb','0xff','0xaa']);
        await gsr.createRecord("name",['0x02','0xff','0xbb','0xff','0xaa','0xff','0xbb','0xff','0xaa','0xff','0xbb','0xff','0xaa','0xff','0xbb','0xff','0xaa']);
        await gsr.createRecord("name",['0x03','0x31','0x32','0x33']);
        await gsr.createRecord("name",['0x03','0x31','0x33','0x33']);

        assert.equal(await gsr.getRecordsCount("name"), 8, "getRecordsCount wrong result");

        const rawRecordAt = await gsr.getRawRecordAt("name",1);
        await gsr.removeRecord("name",rawRecordAt);
        assert.equal(await gsr.getRecordsCount("name"), 7, "removeRecord not work");

        await gsr.createRecord("name",['0x00','0x00','0x00','0x00','0x03','0x37','0x32','0x33']);
        let passed = true;
        try {
            await gsr.createRecord("name",['0x00','0x00','0x00','0x00','0x03','0x37','0x32','0x33']);
            passed=false;
        }catch (_) {}
        if(!passed){
            throw "createRecord can create record not unique";
        }

        assert.equal(await gsr.getRecordsCount("name1"), 1, "getRecordsCount wrong result");
    });

    it("access test", async () => {
        const gsr = await GSR.deployed();

        await gsr.createRecord("access0",['0x00','0x00','0x00','0x00','0x03','0x31','0x32','0x33'],{from:accounts[0]});
        await gsr.createRecord("access1",['0x00','0x00','0x00','0x00','0x03','0x31','0x32','0x33'],{from:accounts[1]});

        // account1 get count records of account0
        await gsr.getRecordsCount("name",{from:accounts[1]});

        {
            let passed = true;
            try {
                await gsr.createRecord("access0",['0x00','0x00','0x00','0x00','0x03','0x31','0x32','0x33'],{from:accounts[1]});
                passed=false;
            }catch (_) {}
            if(!passed){
                throw "createRecord not owner have access";
            }
        }

        {
            try {
                await gsr.getRawRecordAt("name", 1,{from:accounts[1]});
            }catch (_) {
                throw "getRawRecordAt not owner not have access";
            }
        }
    });

    it("name in register", async () => {
        const gsr = await GSR.deployed();

        assert.equal(await gsr.isNameExist("name in register"), false, "isNameExist wrong result");

        await gsr.createRecord("name in register",['0x00','0x00','0x00','0x00','0x03','0x31','0x32','0x33']);

        assert.equal(await gsr.isNameExist("name in register"), true, "isNameExist wrong result");
    });

});