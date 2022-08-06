document.getElementById('demo').innerHTML = 'this is javascript'

var btn = document.getElementById('selectDay15');
console.log('check1')
btn.addEventListener('click', function() {
    console.log('click')
    btn.style.backgroundColor = 'pink';
});
