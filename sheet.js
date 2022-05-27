var ss = SpreadsheetApp.getActiveSpreadsheet()
staff = ss.getSheetByName("工作人員")


function getAllSheetsName(){
  var sheetsname = []
  var sheets = ss.getSheets()
  
  sheets.forEach(function(sheet){
    sheetsname.push(sheet.getName());
  })
  return sheetsname
}

function getStaffName(){
  var staffname = []
  var values = staff.getDataRange().getValues()
  
  for(let i = 0; i<values.length; i++){
    staffname.push(values[i][0])
  }
  return staffname
}

function doPost(e) {
  var msg = JSON.parse(e.postData.contents)
  var groupname = msg.groupname
  var members = msg.members
  var mids = msg.mids
  if(groupname == "管理群"){
    staff.clear()
    for(let i = 0; i<members.length; i++){
      staff.appendRow(['\'' + members[i], mids[i]])
    }
  }else{
    var sheetsname = getAllSheetsName()
    if(sheetsname.includes(groupname)){
      staffname = getStaffName()
      var sheet = ss.getSheetByName(groupname)
      sheet.clear()
      for(let i = 0; i<members.length; i++){
          sheet.appendRow(['\'' + members[i], mids[i]])
      }
    }else{
      staffname = getStaffName()
      var sheet = ss.insertSheet(groupname)
      for(let i = 0; i<members.length; i++){
        sheet.appendRow(['\'' + members[i], mids[i]])
      }
    }
  }

}
