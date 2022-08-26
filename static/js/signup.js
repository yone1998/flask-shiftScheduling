const app = new Vue({
    el: '#app',
    data: {
        name: null
        ,email: null
        ,password: null
        ,passwordCheck: null
        ,isFullTime: null
        ,isNoneName: false
        ,isNoneEmail: false
        ,isNonePassword: false
        ,isNonePasswordCheck: false
        ,isNoneIsFullTime: false
        ,isOverName: false
        ,isNotGoodEmail: false
        ,isUnmatchPassword: false
        ,isOverPassword: false
        ,isOverPasswordCheck: false
    },
    methods:{
        checkForm: function (e) {
            if (
                this.name
                && this.email
                && this.password
                && this.passwordCheck
                && this.isFullTime
                ) {
                if (
                    this.name.length <= 5
                    && this.password === this.passwordCheck
                    && this.password.length <= 20
                    && this.passwordCheck.length <= 20
                    ) {

                    return true;
                }

                if (this.name.length > 5) {
                    this.isOverName = true;
                }
                if (!this.validEmail(this.email)) {
                    this.isNotGoodEmail = true
                }
                if (this.password !== this.passwordCheck) {
                    this.isUnmatchPassword = true;
                }
                if (this.password.length > 20) {
                    this.isOverPassword = true;
                }
                if (this.passwordCheck.length > 20) {
                    this.isOverPasswordCheck = true;
                }

                e.preventDefault();
            }

        if (!this.name) {
            this.isNoneName = true;
        }
        if (!this.email) {
            this.isNoneEmail = true;
        }
        if (!this.password) {
            this.isNonePassword = true;
        }
        if (!this.passwordCheck) {
            this.isNonePasswordCheck = true;
        }
        if (!this.isFullTime) {
            this.isNoneIsFullTime = true;
        }

        e.preventDefault();
        }
        ,validEmail: function (email) {
            var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(email);
        }
    }
    ,watch:{
        name: function (e) {
            if (e.length > 0) {
                this.isNoneName = false;
                this.isOverName = false;
            }
        }
        ,email: function (e) {
            if (e.length > 0) {
                this.isNoneEmail = false;
                this.isNotGoodEmail = false;
            }
        }
        ,password: function (e) {
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
        ,isFullTime: function (e) {
            if (e.length > 0) {
                this.isNoneIsFullTime = false;
            }
        }
    }
})
