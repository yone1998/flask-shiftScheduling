// new Vue({
//     el: '#app'
//     ,data: {
//         message: 'hello world'
//     }
//     ,delimiters: ['[[', ']]']
// })

new Vue({
    delimiters: ['[[', ']]']
    ,el: "#app"
    ,data: {
        event: ''
        ,last: ''
        ,sumFullTime: ''
        ,sumPartTime: ''
        ,sumPartTime_realTime: ''
        ,partStartEndList: []
        ,conditionArr: []
        ,isOpen: true
    }
    ,methods: {
        addCondition: function() {
            const tmp1 = Array(this.sumPartTime_realTime).fill(0);
            const tmp2 = Array(this.sumPartTime_realTime).fill(0);
            this.partStartEndList = [tmp1, tmp2];
            for (let iPart = 0; iPart < this.sumPartTime; iPart++) {
                this.partStartEndList[0][iPart] = Number(document.getElementById('partStartAdd' + (iPart+1)).value)
                this.partStartEndList[1][iPart] = Number(document.getElementById('partEndAdd' + (iPart+1)).value)
                console.log(document.getElementById('partStartAdd' + (iPart+1)).value)
            }
            console.log(this.partStartEndList)
        }
        ,openAndClose: function() {
            console.log(this.isOpen)
            this.isOpen = !this.isOpen
            const element = document.getElementById('openCloseBtnConditions')
            if (this.isOpen) {
                element.style.transform = "translateX(10%) translateY(-40%) rotate(45deg)";
            } else {
                element.style.transform = "rotate(-45deg)";
            }

        }
    }
    ,watch: {
        sumPartTime:function(e){
            this.sumPartTime_realTime = Number(e)
        }
    }
})
