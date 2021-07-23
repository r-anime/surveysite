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

function filterData(rows) {
    let result = [];
    for (let row of rows) {
        if (row["popularity"] > 0.0) {
            result.push(row);
        }
    }
    return result;
}

function rowClass(item, type) {
    if (item["popularity"] < 2.0) {
        return "row-under-threshold";
    }
    else {
        return null;
    }
}

function getTableItems(animeData) {
    const tableItems = [];
    for (let anime_id in animeData) {
        const item = animeData[anime_id];
        item["name"] = animeInfo[anime_id];
        tableItems.push(item);
    }
    return tableItems;
}


const columnTypes = {
    name: {
        key: "name",
        label: "Anime",
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
    column["thClass"] = column["key"] == "name" ? "table-col-name" : "table-col-result";
    column["tdClass"] = column["thClass"];
}

// TODO: Commenting away gender-specific result types is only done
// because the full results table as it is now is simply too wide to fit on the page.
const animeSeriesColumns = [].concat([
    columnTypes["name"],
    columnTypes["popularity"],
    //columnTypes["popularity_male"],
    //columnTypes["popularity_female"],
    columnTypes["gender_popularity_ratio"],
    columnTypes["age"]],
    !surveyIsPreseason ? [
        columnTypes["underwatched"]
    ] : [], [
    columnTypes["score"],
    //columnTypes["score_male"],
    //columnTypes["score_female"],
    columnTypes["gender_score_difference"]],
    !surveyIsPreseason ? [
        columnTypes["surprise"], columnTypes["disappointment"]
    ] : []
);
const specialAnimeColumns = [].concat([
    columnTypes["name"],
    columnTypes["popularity"],
    //columnTypes["popularity_male"],
    //columnTypes["popularity_female"],
    columnTypes["gender_popularity_ratio"],
    columnTypes["age"]],
    !surveyIsPreseason ? [
        columnTypes["score"], columnTypes["gender_score_difference"], //columnTypes["score_male"], columnTypes["score_female"],
    ] : []
);

// TODO: Gender-specific result types are currently not displayed on the full results page,
// so the sorting column has to be the non-gender specific one. See the note above.
if (sortBy === "popularity_male" || sortBy === "popularity_female") {
    sortBy = "popularity";
}
else if (sortBy === "score_male" || sortBy === "score_female") {
    sortBy = "score";
}

new Vue({
    el: "#" + animeSeriesTableId,
    delimiters: ["{$", "$}"],
    data: {
        fields: animeSeriesColumns,
        items: filterData(getTableItems(animeSeriesData)),
        sortBy: sortBy,
        sortDesc: sortBy === "name" ? false : true,
    },
});

let specialCanSortBy = false;
for (let i = 0; i < specialAnimeColumns.length; i++) {
    if (sortBy === specialAnimeColumns[i]["key"]) {
        specialCanSortBy = true;
    }
}
const specialSortBy = specialCanSortBy ? sortBy : "name";
new Vue({
    el: "#" + specialAnimeTableId,
    delimiters: ["{$", "$}"],
    data: {
        fields: specialAnimeColumns,
        items: filterData(getTableItems(specialAnimeData)),
        sortBy: specialSortBy,
        sortDesc: specialSortBy === "name" ? false : true,
    },
});