const columnTypes = {
    rank: {
        key: "rank",
        label: "",
        thClass: "table-col-rank",
        tdClass: "table-col-rank",
    },
    image: {
        key: "image",
        label: "",
        thClass: "table-col-image",
        tdClass: "table-col-image",
    },
    name: {
        key: "name",
        label: "Anime",
        thClass: "table-col-name",
        tdClass: "table-col-name",
    },
    popularity: {
        key: "popularity",
        label: "Pop\u00adu\u00adlar\u00adi\u00adty",
        formatter: percentageFormatter,
    },
    popularity_male: {
        key: "popularity_male",
        label: "Pop\u00adu\u00adlar\u00adi\u00adty (Male)",
        formatter: percentageFormatter,
    },
    popularity_female: {
        key: "popularity_female",
        label: "Pop\u00adu\u00adlar\u00adi\u00adty (Female)",
        formatter: percentageFormatter,
    },
    gender_popularity_ratio: {
        key: "gender_popularity_ratio",
        label: "Gen\u00adder Ra\u00adtio",
        formatter: genderRatioFormatter,
    },
    gender_popularity_ratio_inv: {
        key: "gender_popularity_ratio_inv",
        label: "Gen\u00adder Ra\u00adtio",
        formatter: genderRatioInvFormatter,
    },
    age: {
        key: "age",
        label: "Avg. Age",
        formatter: ageFormatter,
    },
    underwatched: {
        key: "underwatched",
        label: "Un\u00adder\u00adwatch\u00aded",
        formatter: percentageFormatter,
    },
    score: {
        key: "score",
        label: "Score",
        formatter: scoreFormatter,
    },
    score_male: {
        key: "score_male",
        label: "Score (Male)",
        formatter: scoreFormatter,
    },
    score_female: {
        key: "score_female",
        label: "Score (Female)",
        formatter: scoreFormatter,
    },
    gender_score_difference: {
        key: "gender_score_difference",
        label: "Score Diff.",
        formatter: genderScoreDiffFormatter,
    },
    gender_score_difference_inv: {
        key: "gender_score_difference_inv",
        label: "Score Diff.",
        formatter: genderScoreDiffInvFormatter,
    },
    surprise: {
        key: "surprise",
        label: "Sur\u00adprise",
        formatter: percentageFormatter,
    },
    disappointment: {
        key: "disappointment",
        label: "Dis\u00adap\u00adpoint\u00adment",
        formatter: percentageFormatter,
    }
};

for (let column_idx in columnTypes) {
    let column = columnTypes[column_idx];
    column["sortable"] = true;
}

function copyObject(object) {
    const result = {};
    for (let key in object) {
        result[key] = object[key];
    }
    return result;
}

function getTableItems(animeData) {
    const tableItems = [];
    for (let anime_id in animeData) {
        const item = copyObject(animeData[anime_id]);
        item["name"] = animeInfo[anime_id];
        tableItems.push(item);
    }
    return tableItems;
}

function sortCompare(aRow, bRow, key, sortDesc, formatter, compareOptions, compareLocale) {
    const a = aRow[key];
    const b = bRow[key];

    if (key == "name") {
        // Sort names by the first official name (should be the Japanese name).
        const aName = a["official_name_list"][0];
        const bName = b["official_name_list"][0];
        return aName < bName ? -1 : aName > bName ? 1 : 0;
    }
    else if (typeof(a) == "number" && typeof(b) == "number") {
        // Treat NaN as the lowest number possible.
        if (isNaN(a)) return -1;
        if (isNaN(b)) return 1;
        return a < b ? -1 : a > b ? 1 : 0;
    }
    else {
        return null;
    }
}

function setColumnCssClass(column, cssClass) {
    const result = copyObject(column);
    result["tdClass"] = cssClass;
    result["thClass"] = cssClass;
    return result;
}

function processData(tableItems, sortKey, sortDesc, topCount, bottomCount) {
    // Sort.
    tableItems.sort(function(a, b) {
        const comparison = sortCompare(a, b, sortKey);
        return (sortDesc ? -1.0 : 1.0) * (comparison ? comparison : a[sortKey] - b[sortKey]);
    });

    // Filter anime below popularity threshold.
    tableItems = tableItems.filter(function(item) { return item["popularity"] > 2.0});

    // Calculate the min and max values for the progress bar value.
    let pbMin = 0.0;
    let pbMax = 85.0;
    let pbValueConversion = function(value) { return value };
    switch (sortKey) {
        case "score":
        case "score_male":
        case "score_female":
            pbMin = 1.0;
            pbMax = 5.0;
            break;
        case "gender_score_difference":
        case "gender_score_difference_inv":
            pbMax = 1.5;
            pbValueConversion = function(value) { return Math.abs(value) };
            break;
        case "gender_popularity_ratio":
        case "gender_popularity_ratio_inv":
            pbMax = 10.0;
            pbValueConversion = function(value) { return value >= 1.0 ? value : 1.0 / value };
            break;
        case "age":
            pbMin = 20.0;
            pbMax = 30.0;
            break;
    }

    // Add progress bar value and item rank.
    for (let i = 0; i < tableItems.length; i++) {
        let pbValue = pbValueConversion(tableItems[i][sortKey]);
        pbValue = (pbValue - pbMin) / (pbMax - pbMin);
        pbValue = Math.min(Math.max(pbValue, 0.0), 1.0);
        tableItems[i]["pb_width"] = "width:" + String(pbValue * 100.0) + "%;";
        tableItems[i]["rank"] = i + 1;
    }

    // Slice table to only include top X and bottom Y.
    if (typeof(topCount) === "number") {
        if (typeof(bottomCount) === "number") {
            const filler = {
                name: {
                    official_name_list: ["..."],
                    image: null,
                },
            }
            filler[sortKey] = "...";
            return tableItems.slice(0, topCount).concat([filler], tableItems.slice(-bottomCount));
        }
        return tableItems.slice(0, topCount);
    }
    return tableItems;
}