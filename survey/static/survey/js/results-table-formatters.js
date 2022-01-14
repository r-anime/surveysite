function genericNumberFormatter(value, validFormatter) {
    switch (isNaN(value) || value) {
        case true:
            return typeof(value) === "number" ? "N/A" : value;
        case Infinity:
            return "\u221e";
        default:
            return validFormatter(value);
    }
}

function percentageFormatter(value) {
    return genericNumberFormatter(value, function (v) { return parseFloat(v).toFixed(1) + "%" });
}
function genderRatioFormatter(value) {
    return genericNumberFormatter(value, function(v) {
        if (v >= 1.0) {
            return parseFloat(v).toFixed(2) + " M:F";
        }
        else {
            return parseFloat(1.0/v).toFixed(2) + " F:M";
        }
    });
}
function genderRatioInvFormatter(value) {
    return genericNumberFormatter(value, function(v) {
        if (v >= 1.0) {
            return parseFloat(v).toFixed(2) + " F:M";
        }
        else {
            return parseFloat(1.0/v).toFixed(2) + " M:F";
        }
    });
}
function scoreFormatter(value) {
    return genericNumberFormatter(value, function(v) { return parseFloat(v).toFixed(2) });
}
function genderScoreDiffFormatter(value) {
    return genericNumberFormatter(value, function (v) {
        if (v >= 0.0) {
            return parseFloat(v).toFixed(2) + " M";
        }
        else {
            return parseFloat(-v).toFixed(2) + " F";
        }
    });
}
function genderScoreDiffInvFormatter(value) {
    return genericNumberFormatter(value, function (v) {
        if (v >= 0.0) {
            return parseFloat(v).toFixed(2) + " F";
        }
        else {
            return parseFloat(-v).toFixed(2) + " M";
        }
    });
}
function ageFormatter(value) {
    return genericNumberFormatter(value, function(v) { return parseFloat(v).toFixed(2) });
}
