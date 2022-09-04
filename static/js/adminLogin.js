const app = new Vue({
    el: '#app'
    ,data: {
        authenticationCode: null
        ,isNoneAuthenticationCode: false
        ,isShowMessage_authenticationCode: true
    }
    ,methods:{
        checkForm: function (e) {
            if (this.authenticationCode) {
                return true;
            } else {
                this.isNoneAuthenticationCode = true;
                e.preventDefault();
            }
        }
    }
    ,watch:{
        authenticationCode: function (e) {
            if (e.length > 0) {
                this.isNoneAuthenticationCode = false;
                this.isShowMessage_authenticationCode = false;
            }
        }
    }
})
