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
        openAndClose: function(e) {
            this.isOpen = !this.isOpen
            const element = document.getElementById(e.target.id)
            console.log(element)
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
