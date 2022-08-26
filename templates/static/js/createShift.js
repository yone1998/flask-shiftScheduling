new Vue({
    delimiters: ['[[', ']]']
    ,el: "#specialDay"
    ,data: {
        event: ''
        ,day: ''
        ,isAnyNone: false
    }
    ,methods: {
        checkForm: function (e) {
            if (this.event && this.day) {
                return true;
            } else {
                if (!this.event) {
                    this.isAnyNone = true
                }
                if (!this.day) {
                    this.isAnyNone = true
                }

                e.preventDefault();
            }
        }
    }
    ,watch: {
        event: function (e) {
            if (e.length > 0) {
                this.isAnyNone = false;
            }
        }
        ,day: function (e) {
            if (e.length > 0) {
                this.isAnyNone = false;
            }
        }
    }
})
