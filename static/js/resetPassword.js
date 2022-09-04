const app = new Vue({
    el: '#app'
    ,data: {
        password: null
        ,passwordCheck: null
        ,isNonePassword: false
        ,isNonePasswordCheck: false
        ,isUnmatchPassword: false
        ,isOverPassword: false
        ,isOverPasswordCheck: false
    }
    ,methods:{
        checkForm: function (e) {
            if (this.password && this.passwordCheck) {
                if (
                    this.password === this.passwordCheck
                    && this.password.length <= 20
                    && this.passwordCheck.length <= 20
                    ) {
                    console.log('test3')
                    return true;
                } else {
                    if (this.password !== this.passwordCheck) {
                        this.isUnmatchPassword = true;
                    }
                    if (this.password.length > 20) {
                        this.isOverPassword = true;
                    }
                    if (this.passwordCheck.length > 20) {
                        this.isOverPasswordCheck = true;
                    }

                    console.log('test1')
                    e.preventDefault();
                    console.log('test2')
                }
            } else {
                if (!this.password) {
                    this.isNonePassword = true;
                }
                console.log(!this.isNonePasswordCheck)
                if (!this.passwordCheck) {
                    this.isNonePasswordCheck = true;
                }
                e.preventDefault();
            }
        }
    }
    ,watch:{
        password: function (e) {
            if (e.length > 0) {
                this.isNonePassword = false;
                this.isUnmatchPassword = false;
                this.isOverPassword = false;
            }
        }
        ,passwordCheck: function (e) {
            if (e.length > 0) {
                this.isNonePasswordCheck = false;
                this.isUnmatchPassword = false;
                this.isOverPasswordCheck = false;
            }
        }
    }
})
