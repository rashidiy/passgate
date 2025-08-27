Chart.elements.Rectangle.prototype.draw = function () {
    var ctx = this._chart.ctx;
    var vm = this._view;
    var left, right, top, bottom, borderWidth;
    var radius = 5;

    borderWidth = vm.borderWidth;
    left = vm.x - vm.width / 2;
    right = vm.x + vm.width / 2;
    top = vm.y;
    bottom = vm.base;

    var barWidth = Math.abs(left - right);
    var barHeight = Math.abs(top - bottom);
    if (radius > barWidth / 2) radius = barWidth / 2;
    if (radius > barHeight / 2) radius = barHeight / 2;

    ctx.beginPath();
    ctx.fillStyle = vm.backgroundColor;
    ctx.strokeStyle = vm.borderColor;
    ctx.lineWidth = borderWidth;

    ctx.moveTo(left, bottom);

    ctx.lineTo(left, top + radius);

    ctx.quadraticCurveTo(left, top, left + radius, top);

    ctx.lineTo(right - radius, top);

    ctx.quadraticCurveTo(right, top, right, top + radius);

    ctx.lineTo(right, bottom);

    ctx.lineTo(left, bottom);

    ctx.closePath();
    ctx.fill();
    if (borderWidth) {
        ctx.stroke();
    }
};
