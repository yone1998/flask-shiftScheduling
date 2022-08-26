const app = new Vue({
    el: '#app',
    data: {
        email: null
        ,password: null
        ,isNoneEmail: false
        ,isNonePassword: false
    },
    methods:{
        checkForm: function (e) {
            if (this.email && this.password) {
                return true;
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
    }
    ,watch:{
        email: function (e) {
            if (e.length > 0) {
                this.isNoneEmail = false;
            }
        }
        ,password: function (e) {
            if (e.length > 0) {
                this.isNonePassword = false;
            }
        }
    }
})
