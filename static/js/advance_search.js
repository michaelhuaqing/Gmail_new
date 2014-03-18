function AddRow()
{
 //添加一行
 var i =tab1.rows.length;
 var sign="add"+i;
 var content_id_1=i+"-1-content";
 var content_id_2=i+"-2-content";
 var keyword=i;
 var logical_id=i+"-logical";
 var relation_id=i+"-relation";
 var newTr = tab1.insertRow(-1);
 //添加列
 var newTd0 = newTr.insertCell(-1);
 var newTd1 = newTr.insertCell(-1);
 var newTd2 = newTr.insertCell(-1);
 var newTd3 = newTr.insertCell(-1);
 var newTd4 = newTr.insertCell(-1);
 var newTd5 = newTr.insertCell(-1);
 //设置列内容和属性
 newTd0.innerHTML = '<tr><td><input type="checkbox" id="box1" onClick="GetRow()"/ /><input type="hidden" name="add" id='+sign+' /></td>';
 
 newTd1.innerHTML = '<td> <select name='+relation_id+'><option value="and">并且</option><option value="or">或者</option>'+
     '<option value="not">不含</option></select></td>';
	 
 newTd2.innerHTML = '<td> <select name="keyword" id='+keyword+' onChange="Change(this.options[this.selectedIndex].value,this.id)">'+
     '<option value="subject">主题</option><option value="from_">发件人</option>'+
	 '<option value="to">收件人</option><option value="ip">ip地址</option><option value="boby_txt">内容</option>'+
     '<option value="attach_txt">附件</option><option value="start">开始时间</option><option value="end">结束时间</option></select></td>';
	 
 newTd3.innerHTML = '<td> <input type="text" name="content" id='+content_id_1+'></td>';
 
 newTd4.innerHTML ='<td> <select name='+logical_id+'><option value="and">并含</option><option value="or">或含</option>'+
     '<option value="not">不含</option></td></select></td>';
	 
 newTd5.innerHTML ='<td> <input type="text" name="content" id='+content_id_2+'></td></tr>';
}

function Change(a,b)
{
    console.log(a, b);
	var temp_1=b+"-1-content";//组合成对应的文本框的id
	var temp_2=b+"-2-content";
    console.log(temp_1, temp_2);
	var obj_1=document.getElementById(temp_1);
	var obj_2=document.getElementById(temp_2);
	obj_1.name=b+"-1-"+a;
	obj_2.name=b+"-2-"+a;
}
function DelRow()
{
//删除一行
  var selected_boxnum=0;
  var box_obj=document.all("box1");
   for(var i=0;i<box_obj.length;i++)
   {
    if (box_obj[i].checked==true)
    {
      selected_boxnum++;
    }
   }
   if(selected_boxnum==box_obj.length)
   {
     alert('最少要添加一项');
     return;
   }
   else  if(selected_boxnum==0)
   {
     alert('请选择你要删除的信息');
     return;
   }
   else if(selected_boxnum==1)
   {
     for(var i=0;i<box_obj.length;i++)
     {
       if(box_obj[i].checked==true)
       {
        tab1.deleteRow(i+1);
       }
     }
   }
   else if(selected_boxnum>1)
   {
     for(var a=0;a<selected_boxnum;a++)
     {
         for(var i=0;i<box_obj.length;i++)
      {
        if(box_obj[i].checked==true)
        {
         tab1.deleteRow(i+1);
         break;
        }
      }
     }
   }
}
function GetRow()
{
  //获得行索引
  //两个parentElement分别是TD和TR哟，rowIndex是TR的属性
  //this.parentElement.parentElement.rowIndex
  cGetRow=window.event.srcElement.parentElement.parentElement.rowIndex;
}
