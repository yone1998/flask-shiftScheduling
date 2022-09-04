const app = new Vue({
    el: '#app'
    ,data: {
        email: null
        ,password: null
        ,isNoneEmail: false
        ,isNotGoodEmail: false
        ,isNonePassword: false
        ,isOverPassword: false
    }
    ,methods:{
        checkForm: function (e) {
            if (this.email && this.password) {
                if (
                    this.validEmail(this.email)
                    && this.password.length <= 20
                    ) {
                    return true;
                } else {
                    if (!this.validEmail(this.email)) {
                        this.isNotGoodEmail = true
                    }
                    if (this.password.length > 20) {
                        this.isOverPassword = true;
                    }

                    e.preventDefault();
                }
            } else {
                if (!this.email) {
                    this.isNoneEmail = true;
                }
                if (!this.password) {
                    this.isNonePassword = true;
                }

                e.preventDefault();
            }
        }
        ,validEmail: function (email) {
            var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(email);
        }
    }
    ,watch:{
        email: function (e) {
            if (e.length > 0) {
                this.isNoneEmail = false;
                this.isNotGoodEmail = false;
            }
        }
        ,password: function (e) {
            if (e.length > 0) {
                this.isNonePassword = false;
                this.isOverPassword = false;
            }
        }
    }
})
