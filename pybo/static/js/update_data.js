function update_data(data, selected_city){

    let filterData;

    if(selected_city == "전체"){
        filterData = data;
    }else{
        filterData = data.filter(function(obj){
            return obj['시도명'] === selected_city;
        });
    }

    let dtable = $("#dtable tbody");
    dtable.empty();     // 기존 데이터 추기화

    filterData.forEach(function(updateData, index){
        dtable.append(`<tr>
                        <td>${index + 1}</td>
                        <td>${updateData['시도명']}</td>
                        <td>${updateData['시군구']}</td>
                        <td>${updateData['확진자']}</td>
                        <td>${updateData['사망자']}</td>
                    </tr>`);
    });
}