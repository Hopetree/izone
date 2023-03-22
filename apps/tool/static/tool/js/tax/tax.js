class PersonalIncomeTaxSettlement {
    constructor(income, special_deduction, special_add_deduction, annual_bonus = 0.0) {
        /*
        :param income: 累计综合所得收入
        :param special_deduction: 累计专项扣除，也就是每月扣除五险一金的费用的总和
        :param special_add_deduction: 累计专项附加扣除
        :param annual_bonus: 全年一次性奖金收入
        */
        this.income = income;
        this.special_deduction = special_deduction;
        this.special_add_deduction = special_add_deduction;
        this.annual_bonus = annual_bonus;
        this.subtraction = 60000;
    }

    get_accumulative_tax(accumulative_income) {
        /*
        计算综合所得收入的税
        :param accumulative_income: 综合所得收入
        :return:
        */
        let tax;
        if (accumulative_income <= 36000) {
            tax = accumulative_income * 0.03;
        } else if (accumulative_income <= 144000) {
            tax = accumulative_income * 0.1 - 2520;
        } else if (accumulative_income <= 300000) {
            tax = accumulative_income * 0.2 - 16920;
        } else if (accumulative_income <= 420000) {
            tax = accumulative_income * 0.25 - 31920;
        } else if (accumulative_income <= 660000) {
            tax = accumulative_income * 0.3 - 52920;
        } else if (accumulative_income <= 960000) {
            tax = accumulative_income * 0.35 - 85920;
        } else {
            tax = accumulative_income * 0.45 - 181920;
        }
        return tax;
    }

    planA() {
        /*
        方案一：并入综合所得计税
        应纳税额 = （累计综合所得收入 - 累计减除费用 - 累计专项扣除 - 累计专项附加扣除）x 适用税率 - 速算扣除数
        :return:
        */
        const amount = this.income - this.subtraction - this.special_deduction - this.special_add_deduction;
        console.log('并入综合所得计税计算计税额：' + amount);
        const tax = this.get_accumulative_tax(amount);
        console.log('并入综合所得计税计算应缴税为：' + tax);
        const _tax = (tax < 0) ? 0 : tax;
        return _tax.toFixed(2)
    }

    planB() {
        /*
        方案二：做为全年一次性收入，单独计税
        应纳税额 = (全年一次性奖金收入 x 适用税率 - 速算扣除总数) + (全年综合所得-奖金所得)计算重新计算的综合税
        :return:
        */
        const amount = this.income - this.annual_bonus - this.subtraction - this.special_deduction - this.special_add_deduction;
        console.log('年终奖单独计算计税额：' + amount);
        const tax = this.get_accumulative_tax(amount) + this.get_accumulative_tax(this.annual_bonus);
        console.log('年终奖单独计算应缴税：' + tax.toFixed(2));
        const _tax = (tax < 0) ? 0 : tax;
        return _tax.toFixed(2)
    }
}

$('#start-tax').click(function () {
    const income = $('#income').val();
    const old_tax = $('#old_tax').val();
    const special_deduction = $('#special_deduction').val();
    const special_add_deduction = $('#special_add_deduction').val();
    const annual_bonus = $('#annual_bonus').val();
    let lis = [{"desc": "收入合计", "value": income}, {"desc": "已申报税额合计", "value": old_tax},
        {"desc": "专项扣除合计", "value": special_deduction}, {"desc": "专项附加扣除合计", "value": special_add_deduction}];
    for (let i = 0; i < lis.length; i++) {
        let each = lis[i];
        if (!each['value']) {
            alert('🥺【' + each['desc'] + '】' + '为空，无法计算！！！');
            return false
        }
    }
    const personal_tax = new PersonalIncomeTaxSettlement(income, special_deduction, special_add_deduction, annual_bonus)
    const tax_a = personal_tax.planA()
    const tax_b = personal_tax.planB()
    const msg = "【并入综合所得税计算】结果：\n应纳税额：" + tax_a + "\n已缴税额：" + old_tax + "\n可退税额：" + (old_tax - tax_a).toFixed(2) +
        "\n💰---------------------------💰\n" +
        "【年终奖单独计算】结果：\n应纳税额：" + tax_b + "\n已缴税额：" + old_tax + "\n可退税额：" + (old_tax - tax_b).toFixed(2)
    alert(msg)
})