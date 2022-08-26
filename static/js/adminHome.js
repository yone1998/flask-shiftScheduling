new Vue({
    delimiters: ['[[', ']]']
    ,el: "#condition"
    ,data: {
        event: ''
        ,sumFullTime: ''
        ,sumPartTime: ''
        ,isAnyNone: false
    }
    ,methods: {
        checkForm: function (e) {
            if (this.event
                && this.sumFullTime
                && this.sumPartTime
                ) {
                return true;
            } else {
                if (!this.event) {
                    this.isAnyNone = true
                }
                if (!this.sumFullTime) {
                    this.isAnyNone = true
                }
                if (!this.sumPartTime) {
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
        ,sumFullTime: function (e) {
            if (e.length > 0) {
                this.isAnyNone = false;
            }
        }
        ,sumPartTime: function (e) {
            // このメソッドを実行するとループに反映されるが、もっときれいに書く方法がわからない
            this.sumPartTime = Number(e)
            if (e.length > 0) {
                this.isAnyNone = false;
            }
        }
    }
})
