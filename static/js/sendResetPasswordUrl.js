new Vue({
    el: '#app'
    ,data: {
        email: null
        ,isNoneEmail: false
        ,isNotGoodEmail: false
    }
    ,methods:{
        checkForm: function (e) {
            if (this.email) {
                if (this.validEmail(this.email)) {
                    return true;
                } else {
                    this.isNotGoodEmail = true;
                    e.preventDefault();
                }
            } else {
                this.isNoneEmail = true;
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
    }
})
