/*
Correlation Plots for Phenotype-Phenotype Overlaps 
author: Dominik Grimm
*/
function corrPlot() {
	var __plot = {};
	var __container = "body";
	var __container_scatter = "body";
	var __container_venn = "body";
	var __duration = 1500;
    var __colorbarwidth = 25;
    var __colorbarpadding = 10;
    var __width = 500;
    var __height = 610;
    var __width_scatter=__width, __height_scatter=__height*3/6;
	var __margins = {top: 100, bottom: 25, left: 120, right: 80};
	var __margins_scatter = {top: 10, bottom: 50, left: 50, right: 20};
    var __colors = d3.scale.quantize().domain([-1,1]).range(['#0B3568','#1E4371','#32527A','#456183','#59708C',
                                                             '#6C7F96','#808E9F','#939DA8','#A7ACB1','#BBBBBB',
                                                             '#BBAAAA','#B2979A','#A9858B','#A1737B','#98606C',
                                                             '#904E5C','#873C4D','#873C4D','#7F293D','#6E051F']);
    var __axes_data = [];
    var __data_matrix = [];
    var __spear_matrix = [];
    var __data = [];
    var __data_scatter = [];
    var __data_venn = [];
	var __svg, __box_g, __svg_scatter, __scatter_g, __axes_scatter;
	var __x_scale, __y_scale, __x_scale_scatter, __y_scale_scatter;
    var __x_axis_scatter,__y_axis_scatter;
    var __size_scale, __highlight_scale;
    var __info_box;
    var __svg_venn, __venn_g, __venn_chart;
    var __mapping;
    var __method = "pearson";

	__plot.render = function() {
        if (!__container) __container = "body";
        if (!__container_scatter) __container_scatter = "body";
        if (!__width) {
            __width = d3.select(__container).style('width').replace("px","");
            __width_scatter = d3.select(__container_scatter).style('width').replace("px","");
        }
        /*
        *Create SVG container if the container does not exist already
        **/
        if (!__svg) {
            __svg = d3.select(__container).append("svg")
                      .attr("height",__height).attr("width",__width);
        }
        
        if (!__svg_scatter) {
            __svg_scatter = d3.select(__container_scatter).append("svg")
                      .attr("height",__height_scatter).attr("width",__width_scatter);
        }
        
        if (!__svg_venn) {
            __svg_venn = d3.select(__container_venn).append("svg")
                      .attr("height",__height/3).attr("width",__width_scatter);
        }

		//PREPARE DATA
        var pheno_ids = [];
        __mapping = {};
        __data_matrix = JSON.parse(__data_matrix)
        __spear_matrix = JSON.parse(__spear_matrix)
        for (var i=0; i<__axes_data.length; i++) {
            pheno_ids.push(__axes_data[i].pheno_id);
            //if(!__axes_data[i].pheno_id in __mapping) {
            __mapping[__axes_data[i].pheno_id] = __axes_data[i].label.substring(0,22) + "...";
            //}
            for (var j=0; j<__axes_data.length;j++){
                if(i==j) continue;
                if(isNaN(__data_matrix[__axes_data[i].index][__axes_data[j].index])) continue;
                __data.push({"i":i,
                             "j":j,
                             "x_pheno_id":__axes_data[i].pheno_id, 
                             "y_pheno_id":__axes_data[j].pheno_id, 
                             "x_label":__axes_data[i].label,
                             "y_label":__axes_data[j].label,
                             "corr":__data_matrix[__axes_data[i].index][__axes_data[j].index],
                             "spear":__spear_matrix[__axes_data[i].index][__axes_data[j].index]});
            }
        }
	    __x_scale = d3.scale.ordinal().domain(pheno_ids).rangeRoundBands([0,getContainerWidth()]);
        __y_scale = d3.scale.ordinal().domain(pheno_ids).rangeRoundBands([0,getContainerHeight()]);
    
        __x_scale_scatter = d3.scale.linear().domain([0,1]).range([0,getContainerWidthScatter()]);
        __y_scale_scatter = d3.scale.linear().domain([1,0]).range([0,getContainerHeightScatter()]);
        
        var rb = __x_scale.rangeBand()/2*0.8;
        __size_scale = d3.scale.quantize().domain([-1,1]).range([rb,rb*0.9,rb*0.8,rb*0.7,rb*0.6,rb*0.5,rb*0.4,rb*0.3,rb*0.2,rb*0.1,
                            rb*0.1,rb*0.2,rb*0.3,rb*0.4,rb*0.5,rb*0.6,rb*0.7,rb*0.8,rb*0.9,rb]);
        __highlight_scale = d3.scale.quantize().domain([-1,1]).range([rb]);

		/*
		Plot coordinate System
		*/
		axes = renderCoordinateSystem();
        /*
        *Render Colorbar
        */
        renderColorBar(axes);
		/*
		Render data
		 */
        renderCorrPlot(axes);

        /*CREATE associated scatter plot*/
        renderScatterCoordinateSystem();

	};

    function renderColorBar(axes) {
        var colorbar_g = axes.append("g").attr("class","colorbar")
				.attr("transform",function() {
					return "translate(" + __margins.left + "," + __margins.top + ")";        
				 });
        var sn = 20;
        var colorbar_box = colorbar_g
            .append("rect").attr("class","colorborder")
            .attr("width",__colorbarwidth)
            .attr("height",getContainerHeight())
            .attr("x",getContainerWidth()+__colorbarpadding/2)
            .attr("y",0)
            .style("fill","none").style("stroke","#000")
            .style("stroke-width","2px")
            .style("shape-rendering","crispEdges");

        var colorbar = colorbar_g.selectAll("rect.colorbar")
                .data(d3.range(-1,1,2/sn+0.001)).enter()
                .append("rect")
                .attr("class",function(d,i){return "colorbar_" + __colors(d).replace("#","");})
                .attr("width",__colorbarwidth)
                .attr("height",getContainerHeight()/sn)
                .attr("x", getContainerWidth()+__colorbarpadding/2)
                .attr("y",function(d,i){
                    return getContainerHeight() - (i+1)*getContainerHeight()/sn;
                })
                .style("fill",function(d,i){return __colors(d)})
                .style("fill-opacity",0);

        colorbar.transition().duration(__duration)
            .style("fill-opacity",1);
        
        var color_axis = d3.svg.axis().scale(d3.scale.linear().domain([1,-1]).range([0,getContainerHeight()])).orient("right");
        colorbar_g.append("g").attr("class","color axis")
			.attr("transform",function() {
			    return "translate(" + (getContainerWidth() + __colorbarpadding/2 + __colorbarwidth) +  ",0)";        
			})
            .call(color_axis);
        colorbar_g.selectAll(".axis path, .axis line").style({"fill": "none","stroke":"black","shape-rendering":"crispEdges"});
        colorbar_g.selectAll(".axis text").style({"font-family":"Myriad Pro, Arial, Garuda, Garuda, Helvetica, Tahoma, sans-serif","font-size":"12px"});
        colorbar_g.selectAll(".axis, .grid-line").style({"stroke":"black","shape-rendering":"crispEdges","stroke-opacity":"0.2"});
        
		var colorbar_label = colorbar_g.append("text").attr("class","colorbar label")
            .attr("transform","rotate(-90)")
            .attr("y",getContainerWidth()+__colorbarpadding/2+__colorbarwidth+2*__colorbarpadding)
            .attr("x",-getContainerHeight()/2)
            .attr("dy","1.4em").style("text-anchor","middle").text("Pearson Correlation");

        colorbar.on("mouseover",function(d) {
            d3.select(this)
                .transition().duration(100)
                .style("fill-opacity","0.2");
            d3.selectAll(".corr_color_" + __colors(d).replace("#",""))
                .transition().duration(100)
                .attr("r",__highlight_scale(d))
                .style("font-size","18px")
                .style("fill-opacity",0.9);

        }).on("mouseout",function(d) {
            d3.select(this)
                .transition().duration(100)
                .style("fill-opacity",1);
            d3.selectAll(".corr_color_" + __colors(d).replace("#",""))
                .transition().duration(100)
                .attr("r",__size_scale(d))
                .style("font-size","12px")
                .style("fill-opacity",1);
        
        })
        

    }
    
    function renderScatterCoordinateSystem() {
		if(!__axes_scatter) __axes_scatter = __svg_scatter.append("g").attr("class","axes scatter");

		//create axis
		__x_axis_scatter = d3.svg.axis().scale(__x_scale_scatter).orient("bottom");
		__y_axis_scatter = d3.svg.axis().scale(__y_scale_scatter).orient("left");
		
        //render axis
		__axes_scatter
                .append("g")
                .attr("class","xs axis")
				.attr("transform",function() {
					return "translate(" + __margins_scatter.left + "," + (__height_scatter-__margins_scatter.bottom) + ")";        
				 })
			.call(__x_axis_scatter);

		__axes_scatter.append("g").attr("class","ys axis")
				.attr("transform",function() {
					return "translate(" + __margins_scatter.left + "," + __margins_scatter.top + ")";        
				 })
			.call(__y_axis_scatter);
        
        //render grid
        var grid_x = d3.selectAll("g.xs g.tick")
                        .append("line")
                        .attr("class","grid-line scatter")
                        .attr("x1",0)
                        .attr("y1",0)
                        .attr("x2",0)
                        .attr("y2", -getContainerHeightScatter())
                        .style("stroke-opacity","0.2");
        
        var grid_y = d3.selectAll("g.ys g.tick")
                        .append("line")
                        .attr("class","grid-line scatter")
                        .attr("x1",0)
                        .attr("y1",0)
                        .attr("x2",getContainerWidthScatter())
                        .attr("y2",0)
                        .style("stroke-opacity","0.2");

        //render labels
        __axes_scatter.append("text").attr("class","scatter_x_label").attr("text-anchor","middle")
            .attr("x",(__width_scatter/2.0)).attr("y",__height_scatter-__margins_scatter.bottom)
            .attr("dy","3.2em")
            .style("font-size","12px")
            .text("");
        
        __axes_scatter.append("text").attr("class","scatter_y_label").attr("text-anchor","middle")
            .attr("transform","rotate(-90)")
            .attr("x",(-__height_scatter/2)).attr("y",__margins_scatter.left)
            .attr("dy","-3.2em")
            .attr("dx","-.5em")
            .style("font-size","12px")
            .text("");
        
        __axes_scatter.selectAll(".axis path, .axis line").style({"fill": "none","stroke":"black","shape-rendering":"crispEdges"});
		__axes_scatter.selectAll(".axis text").style({"font-family":"Myriad Pro, Arial, Garuda, Garuda, Helvetica, Tahoma, sans-serif","font-size":"12px"});
		__axes_scatter.selectAll(".axis, .grid-line").style({"stroke":"black","shape-rendering":"crispEdges","stroke-opacity":"0.2"});

        //add info box
        __info_box = __axes_scatter.append("g")
            .attr("class","info_box")
            
        __info_box.append("rect")
            .attr("x",(__width_scatter/2.0)-100)
            .attr("y",__height_scatter/2-50)
            .attr("height",100).attr("width",200)
            .attr("rx",10).attr("ry",10)
            .style("fill","rgb(121,85,72)")
            .style("opacity",0)
            .transition().duration(__duration)
            .style("opacity",0.7)
            
        __info_box.append("text")
            .attr("x",(__width_scatter/2.0))
            .attr("y",__height_scatter/2+0)
            .attr("dy","-1.8em")
            .attr("text-anchor","middle")
            .text("To update scatter plot")
            .style("opacity",0)
            .transition().duration(__duration)
            .style("opacity",1)
            .style("text-width","bold");
        __info_box.append("text")
            .attr("x",(__width_scatter/2.0))
            .attr("y",__height_scatter/2+0)
            .attr("dy","-0.5em")
            .attr("text-anchor","middle")
            .text("hover over any point")
            .style("opacity",0)
            .transition().duration(__duration)
            .style("opacity",1)
            .style("text-width","bold");
        __info_box.append("text")
            .attr("x",(__width_scatter/2.0))
            .attr("y",__height_scatter/2+0)
            .attr("dy","0.8em")
            .attr("text-anchor","middle")
            .text("in the correlation plot")
            .style("opacity",0)
            .transition().duration(__duration)
            .style("opacity",1)
            .style("text-width","bold");
        __info_box.append("text")
            .attr("x",(__width_scatter/2.0))
            .attr("y",__height_scatter/2+0)
            .attr("dy","2.1em")
            .attr("text-anchor","middle")
            .text("in the left panel!")
            .style("opacity",0)
            .transition().duration(__duration)
            .style("opacity",1)
            .style("text-width","bold");
	};

	function renderCoordinateSystem() {
		var axes_g = __svg.append("g").attr("class","axes");

        var coord = axes_g.append("rect").attr("class","coord")
				.attr("transform",function() {
					return "translate(" + __margins.left + "," + (__margins.top) + ")";        
				 })
                .attr("x",0).attr("y",0).attr("width",getContainerWidth())
                .attr("height",getContainerHeight())
                .style("fill","none")
                .style("shape-rendering","crispEdges");
		//create axis
		var x_axis = d3.svg.axis().scale(__x_scale).orient("top").tickFormat(function(d){return __mapping[d];});
	    var y_axis = d3.svg.axis().scale(__y_scale).orient("left").tickFormat(function(d){return __mapping[d];})
		
        //render axis
		axes_g.append("g").attr("class","x axis")
				.attr("transform",function() {
					return "translate(" + __margins.left + "," + (__margins.top) + ")";        
				 })
			.call(x_axis)
            .style("stroke-opacity","0.2")
            .selectAll("text")
                .attr("class",function(d,i){
                    for(var j=0;j<__axes_data.length;j++) {
                        if(__axes_data[j].label==d) return "xtick_" + __axes_data[j].pheno_id;
                    }
                })
                .style("text-anchor", "start")
                .attr("dx", "-0.5em")
                .attr("dy", "-0.5em")
                .attr("transform", function(d) {
                    return "rotate(-45)"; 
                })

		axes_g.append("g").attr("class","y axis")
				.attr("transform",function() {
					return "translate(" + __margins.left + "," + __margins.top + ")";        
				 })
			.call(y_axis)
            .style("stroke-opacity","0.2")
            .selectAll("text")
                .attr("class",function(d,i){
                    for(var j=0;j<__axes_data.length;j++) {
                        if(__axes_data[j].label==d) return "ytick_" + __axes_data[j].pheno_id;
                    }
            })
            .attr("dx", "0.8em")
            .attr("dy", "-1.6em")
            .attr("transform", function(d) {
                return "rotate(-45)"; 
            })
	
        axes_g.selectAll(".axis path, .axis line").style({"fill": "none","stroke":"black","shape-rendering":"crispEdges"});
		axes_g.selectAll(".axis text").style({"font-family":"Myriad Pro, Arial, Garuda, Garuda, Helvetica, Tahoma, sans-serif","font-size":"12px"});
		axes_g.selectAll(".axis, .grid-line").style({"stroke":"black","shape-rendering":"crispEdges","stroke-opacity":"0.2"});
        
        //render grid
        var grid_x = d3.selectAll("g.x g.tick")
                        .append("line")
                        .attr("class","grid-line")
                        .attr("x1",__x_scale.rangeBand()/2)
                        .attr("y1",0)
                        .attr("x2",__x_scale.rangeBand()/2)
                        .attr("y2",  getContainerHeight());
        
        var grid_y = d3.selectAll("g.y g.tick")
                        .append("line")
                        .attr("class","grid-line")
                        .attr("x1",0)
                        .attr("y1",__y_scale.rangeBand()/2)
                        .attr("x2",getContainerWidth())
                        .attr("y2",__y_scale.rangeBand()/2);

        return axes_g;
	};

    function renderCorrPlot(axes) {
        if(!__box_g) {
            __box_g = axes.append("g").attr("class","corrplot")
				.attr("transform",function() {
					return "translate(" + __margins.left + "," + __margins.top + ")";        
				 });
        }

        var circles = __box_g.selectAll("circle corr")
                        .data(__data).enter()
                        .append("circle")
                        .filter(function(d,i){
                            return d.i > d.j;
                        })
                        .attr("class",function(d,i){
                            return "corr " + "corr_color_" + __colors(d.corr).replace("#","") + " id_" + d.i + "_" + d.j;
                        })
                        .attr("cx",function(d,i){
                            return __x_scale(d.x_pheno_id) + (__x_scale.rangeBand()/2);
                        })
                        .attr("cy",function(d,i){
                            return __y_scale(d.y_pheno_id) + (__y_scale.rangeBand()/2);
                        })
                        .attr("r",function(d){return __size_scale(d.corr);})
                        .style("fill",function(d){return __colors(d.corr);})
                        .style("opacity",0);

        circles.transition().duration(__duration)
            .style("cursor","pointer")
            .style("opacity",1);
        
        circles.on("mouseover",function(d,i){
            //d3.selectAll(".corr_color_" + __colors(d.corr).replace("#",""))
            d3.select(this)
                .transition().duration(100)
                .attr("r",__highlight_scale(d.corr))
                .style("fill-opacity",0.9);
            d3.selectAll(".id_" + d.j + "_" + d.i)
                .transition().duration(100)
                .style("font-size","18px")
                .style("fill-opacity",0.9);
            d3.select(".colorbar_" + __colors(d.corr).replace("#",""))
                .transition().duration(100)
                .style("fill-opacity","0.2");
            //update scatter plot
            d3.selectAll(".info_box").transition().duration(200).style("opacity",0);
            
            /*Update associated plots*/
            updateScatterPlot(d.x_pheno_id,d.y_pheno_id);
            updateVennPlot(d.x_pheno_id,d.y_pheno_id);

        }).on("mouseout",function(d,i){
            d3.select(this)
                .transition().duration(100)
                .attr("r",__size_scale(d.corr))
                .style("fill-opacity",1);
            d3.selectAll(".id_" + d.j + "_" + d.i)
                .transition().duration(100)
                .style("font-size","12px")
                .style("fill-opacity",1);
            d3.select(".colorbar_" + __colors(d.corr).replace("#",""))
                .transition().duration(100)
                .style("fill-opacity",1);
        })

        var corr_text = __box_g.selectAll("text tcorr")
                    .data(__data).enter()
                    .append("text")
                    .filter(function(d,i){
                        return d.i < d.j;
                    })
                    .attr("class",function(d,i){
                        return "tcorr " + "corr_color_" + __colors(d.corr).replace("#","") + " id_" + d.i + "_" + d.j;
                    })
                    .attr("x",function(d,i){
                        return __x_scale(d.x_pheno_id) + (__x_scale.rangeBand()/2);
                    })
                    .attr("y",function(d,i){
                        return __y_scale(d.y_pheno_id) + (__y_scale.rangeBand()/2);
                    })
                    .text(function(d){return d.corr.toFixed(2);})
                    .style("text-anchor","middle")
                    .style("font-size","12px")
                    .style("fill",function(d,i){return __colors(d.corr)})
                    .style("opacity",0);

        corr_text.transition().duration(__duration)
            .style("cursor","pointer")
            .style("opacity",1);
        
        corr_text.on("mouseover",function(d,i){
            d3.selectAll(".id_" + d.j + "_" + d.i)
                .transition().duration(100)
                .attr("r",__highlight_scale(d.corr))
                .style("fill-opacity",0.9);
            d3.select(this)
                .transition().duration(100)
                .style("fill-opacity",0.9)
                .style("font-size","18px");
            d3.select(".colorbar_" + __colors(d.corr).replace("#",""))
                .transition().duration(100)
                .style("fill-opacity","0.2");
            d3.selectAll(".info_box").transition().duration(200).style("opacity",0);
            
            /*Update associated plots*/
            updateScatterPlot(d.x_pheno_id,d.y_pheno_id);
            updateVennPlot(d.x_pheno_id,d.y_pheno_id);
        
        }).on("mouseout",function(d,i){
            d3.selectAll(".id_" + d.j + "_" + d.i)
                .transition().duration(100)
                .attr("r",__size_scale(d.corr))
                .style("fill-opacity",1);
            d3.select(this)
                .transition().duration(100)
                .style("font-size","12px")
                .style("fill-opacity",1);
            d3.select(".colorbar_" + __colors(d.corr).replace("#",""))
                .transition().duration(100)
                .style("fill-opacity",1);
        });
        return __plot;
    }

    /*UPDATE SCATTER PLOT*/
    function updateScatterPlot(pheno_id_x,pheno_id_y) {
        if(!__scatter_g) {
            __scatter_g = __axes_scatter.append("g").attr("class","scatterplot")
				.attr("transform",function() {
					return "translate(" + __margins_scatter.left + "," + __margins_scatter.top + ")";        
				 });
        }
        
        var x,y, samples_x, samples_y,label_x,label_y;
        for(var i=0;i<__data_scatter.length;i++) {
            if(__data_scatter[i].pheno_id==pheno_id_x) {
                x = __data_scatter[i].values;
                samples_x = __data_scatter[i].samples;
                label_x = __data_scatter[i].label;
            }
            if(__data_scatter[i].pheno_id==pheno_id_y) {
                y = __data_scatter[i].values;
                samples_y = __data_scatter[i].samples;
                label_y = __data_scatter[i].label;
            }
        }
        //update labels
        d3.select(".scatter_x_label").transition().duration(100)
            .text(label_x);
        d3.select(".scatter_y_label").transition().duration(100)
            .text(label_y);
        

        //match samples
        var data = []
        for(var i=0; i<samples_x.length;i++) {
            var ind = samples_y.indexOf(samples_x[i])
            if(ind!=-1) {
                data.push({x:x[i],y:y[ind]});
            }
        }
        
        //transform axes
        __x_scale_scatter = d3.scale.linear().domain([d3.min(x)-Math.abs(d3.min(x)*0.1),d3.max(x)+Math.abs(d3.min(x)*0.1)])
                                .range([0,getContainerWidthScatter()]);
        __y_scale_scatter = d3.scale.linear().domain([d3.max(y)+Math.abs(d3.min(y)*0.1),d3.min(y)-Math.abs(d3.min(y)*0.1)])
                                .range([0,getContainerHeightScatter()]);
		
        __x_axis_scatter = d3.svg.axis().scale(__x_scale_scatter).orient("bottom");
		__y_axis_scatter = d3.svg.axis().scale(__y_scale_scatter).orient("left");

        
        //d3.select(".xs")
        //d3.select(".ys")
        d3.select(".xs").transition().duration(500).call(__x_axis_scatter).selectAll(".grid-line.scatter").remove();
        d3.select(".ys").transition().duration(500).call(__y_axis_scatter).selectAll(".grid-line.scatter").remove();
    
        d3.selectAll("g.xs g.tick")
                        .append("line")
                        .attr("class","grid-line scatter")
                        .attr("x1",0)
                        .attr("y1",0)
                        .attr("x2",0)
                        .attr("y2", -getContainerHeightScatter());

        d3.selectAll("g.ys g.tick")
                        .append("line")
                        .attr("class","grid-line scatter")
                        .attr("x1",0)
                        .attr("y1",0)
                        .attr("x2",getContainerWidthScatter())
                        .attr("y2",0);
        
        __scatter_g.selectAll("circle.pp")
            .data(data).enter()
            .append("circle")
            .attr("class","pp");
        
        __scatter_g.selectAll("circle.pp")
            .data(data).exit().remove();
        
        __scatter_g.selectAll("circle.pp")
            .data(data)
            .style("stroke",'rgb(121,85,72)')
            .style("fill","rgb(161,136,127)")
            .style("opacity","0.4")
            .style("shape-rendering","crispEdges")
            .transition().duration(500)
            .attr("cx",function(d){return __x_scale_scatter(d.x);})
            .attr("cy",function(d){return __y_scale_scatter(d.y);})
            .attr("r",5);
        
        d3.selectAll(".axis path, .axis line").style({"fill": "none","stroke":"black","shape-rendering":"crispEdges"});
		d3.selectAll(".axis text").style({"font-family":"Myriad Pro, Arial, Garuda, Garuda, Helvetica, Tahoma, sans-serif","font-size":"12px"});
		d3.selectAll(".axis, .grid-line").style({"stroke":"black","shape-rendering":"crispEdges","stroke-opacity":"0.2"});

    }

    function updateVennPlot(pheno_id_x,pheno_id_y) {
    
        var A,B,C;
        var label_x, label_y;
        for(var i=0;i<__data_venn.length;i++){
            if(__data_venn[i].labelA_id==pheno_id_x && __data_venn[i].labelB_id==pheno_id_y) {
                A = __data_venn[i].A;
                B = __data_venn[i].B;
                C = __data_venn[i].C;
                label_x = __data_venn[i].labelA;
                label_y = __data_venn[i].labelB;
            }
            else if(__data_venn[i].labelA_id==pheno_id_y && __data_venn[i].labelB_id==pheno_id_x) {
                A = __data_venn[i].B;
                B = __data_venn[i].A;
                C = __data_venn[i].C;
                label_x = __data_venn[i].labelB;
                label_y = __data_venn[i].labelA;
            }
        }
        
        var sets = [{sets: [label_x], size:A},
                    {sets: [label_y], size:B},
                    {sets: [label_x,label_y], size:C}];
        
        var colors = [__colors(-1),__colors(1)];

        var rm = (__height/6)-10;
        var radius_scale = d3.scale.quantize().domain([d3.min([A,B]),d3.max([A,B])]).range([rm*0.1,rm*0.2,rm*0.3,rm*0.4,rm*0.5,rm*0.6,rm*0.7,rm*0.8,rm*0.9,rm]);
        
        if(C>0 ) {
            d3.select(__container_venn).select("svg").remove();
            d3.select(__container_venn).select("svg").selectAll(".vennA").remove();
            d3.select(__container_venn).select("svg").selectAll(".vennB").remove();
            var venn_chart = venn.VennDiagram()
                .width(__width_scatter).height(__height/3);
            d3.select(__container_venn).datum(sets).call(venn_chart);

            d3.select(__container_venn).selectAll(".venn-circle path")
                .style("fill",function(d,i){return colors[i];})
                
            d3.select(__container_venn).selectAll(".venn-circle text")
                .style("font-size","8px")
                .style("fill","#000");
        } else {
            d3.select(__container_venn).select("svg").remove();
            var svg_venn = d3.select(__container_venn).append("svg")
                .attr("height",__height/3).attr("width",__width_scatter);
            if(C==A && C==B) {
                svg_venn.selectAll("circle.vennA")
                        .data([A]).enter()
                        .append("circle").attr("class","vennA")

                svg_venn.selectAll("circle.vennA")
                        .data([A])
                        .style("fill","steelblue")
                        .style("fill-opacity","0")
                        .transition().duration(100)
                        .attr("cx",__width/2)
                        .attr("cy",__height/6)
                        .attr("r",__height/6-10)
                        .style("fill-opacity","0.25")
                
                svg_venn.selectAll("text.vennA")
                        .data([A]).enter()
                        .append("text").attr("class","vennA")
                        .style("font-size","12px")
                        .transition().duration(100)
                        .attr("x",__width/2)
                        .attr("y",__height/6)
                        .attr("dy","-1em")
                        .style("text-anchor","middle")
                        .text(label_x);
                
                svg_venn.selectAll("text.vennB")
                        .data([B]).enter()
                        .append("text").attr("class","vennB")
                        .style("font-size","12px")
                        .transition().duration(100)
                        .attr("x",__width/2)
                        .attr("y",__height/6)
                        .attr("dy","1em")
                        .style("text-anchor","middle")
                        .text(label_y);

            } else {
                svg_venn.selectAll("circle.vennA")
                        .data([A]).enter()
                        .append("circle").attr("class","vennA")

                svg_venn.selectAll("circle.vennA")
                        .data([A])
                        .style("fill","steelblue")
                        .style("fill-opacity","0")
                        .transition().duration(100)
                        .attr("cx",__width/2-100)
                        .attr("cy",__height/6)
                        .attr("r",__height/6-10)
                        .style("fill-opacity","0.25")

                svg_venn.selectAll("text.vennA")
                        .data([A]).enter()
                        .append("text").attr("class","vennA")
                        .style("font-size","12px")
                        .transition().duration(100)
                        .attr("x",__width/2-100)
                        .attr("y",__height/6)
                        .style("text-anchor","middle")
                        .text(label_x);
                
                svg_venn.selectAll("circle.vennB")
                        .data([B]).enter()
                        .append("circle").attr("class","vennB")

                svg_venn.selectAll("circle.vennB")
                        .data([B])
                        .style("fill","steelblue")
                        .style("fill-opacity","0")
                        .transition().duration(100)
                        .attr("cx",__width/2+100)
                        .attr("cy",__height/6)
                        .attr("r",__height/6-10)
                        .style("fill-opacity","0.25")
                
                svg_venn.selectAll("text.vennB")
                        .data([A]).enter()
                        .append("text").attr("class","vennA")
                        .style("font-size","12px")
                        .transition().duration(100)
                        .attr("x",__width/2+100)
                        .attr("y",__height/6)
                        .style("text-anchor","middle")
                        .text(label_y);

            }
        }

        d3.select(__container_venn).select("svg")
            .selectAll("text.legend.venn").data(sets).enter()
            .append("text").attr("class","legend venn")
 
        d3.select(__container_venn).select("svg")
            .selectAll("text.legend.venn").data(sets).exit().remove()
            
        d3.select(__container_venn).select("svg")
            .selectAll("text.legend.venn").data(sets)
            .attr("x",__width_scatter)
            .attr("y",function(d,i){return 15+i*20;})
            .attr("dx","-10px")
            .text(function(d,i){
                if(d.sets.length==1) {
                    return d.sets[0] + ": " + d.size;
                } else {
                    return "Intersection: " + d.size;
                }
            })
            .style("text-anchor","end")
            .style("font-size","11px")
            .style("fill",function(d,i){
                if(d.sets.length==1){
                    return colors[i];
                }
            })
            .style("font-weight","bold")
    }

	//HELPER FUNCTIONS
	function getContainerWidth() {
		return __width - __margins.left - __margins.right;
	}
	
    function getContainerWidthScatter() {
		return __width_scatter - __margins_scatter.left - __margins_scatter.right;
	}

	function getContainerHeight() {
		return __height - __margins.top - __margins.bottom;
	}
	
    function getContainerHeightScatter() {
		return __height_scatter - __margins_scatter.top - __margins_scatter.bottom;
	}

    __plot.changeCorrMethod = function(method) {
        if (method=="spearman") {
            __method = method;
            d3.selectAll("circle.corr").transition().duration(500)
                .filter(function(d,i) {
                    return d.i > d.j;
                })
                .attr("class",function(d,i) {
                    return "corr " + "corr_color_" + __colors(d.spear).replace("#","") + " id_" + d.i + "_" + d.j;
                })
                .attr("r",function(d){return __size_scale(d.spear*2);})
                .attr("fill",function(d){return __colors(d.spear*2);})
            
            d3.selectAll("text.tcorr").transition().duration(500)
                .filter(function(d,i) {
                    return d.i < d.j;
                })
                .attr("class",function(d,i) {
                    return "tcorr " + "corr_color_" + __colors(d.spear).replace("#","") + " id_" + d.i + "_" + d.j;
                })
                .text(function(d){return d.spear.toFixed(2);})
                .style("fill",function(d,i){return __colors(d.spear)});
    
        corr_text= d3.select("text.colorbar.label")
        corr_text.text("Spearman Correlation")
        
        corr_text.on("mouseover",function(d,i){
            d3.selectAll(".id_" + d.j + "_" + d.i)
                .transition().duration(100)
                .attr("r",__highlight_scale(d.spear))
                .style("fill-opacity",0.9);
            d3.select(this)
                .transition().duration(100)
                .style("fill-opacity",0.9)
                .style("font-size","18px");
            d3.select(".colorbar_" + __colors(d.spear).replace("#",""))
                .transition().duration(100)
                .style("fill-opacity","0.2");
            d3.selectAll(".info_box").transition().duration(200).style("opacity",0);
            
            /*Update associated plots*/
            updateScatterPlot(d.x_pheno_id,d.y_pheno_id);
            updateVennPlot(d.x_pheno_id,d.y_pheno_id);
        
        }).on("mouseout",function(d,i){
            d3.selectAll(".id_" + d.j + "_" + d.i)
                .transition().duration(100)
                .attr("r",__size_scale(d.spear))
                .style("fill-opacity",1);
            d3.select(this)
                .transition().duration(100)
                .style("font-size","12px")
                .style("fill-opacity",1);
            d3.select(".colorbar_" + __colors(d.spear).replace("#",""))
                .transition().duration(100)
                .style("fill-opacity",1);
        });
        } else {
            __method = "pearson";
            d3.selectAll("circle.corr").transition().duration(500)
                .filter(function(d,i) {
                    return d.i > d.j;
                })
                .attr("class",function(d,i) {
                    return "corr " + "corr_color_" + __colors(d.corr).replace("#","") + " id_" + d.i + "_" + d.j;
                })
                .attr("r",function(d){return __size_scale(d.corr);})
                .attr("fill",function(d){return __colors(d.corr);})

            d3.selectAll("text.tcorr").transition().duration(500)
                .filter(function(d,i) {
                    return d.i < d.j;
                })
                .attr("class",function(d,i) {
                    return "tcorr " + "corr_color_" + __colors(d.corr).replace("#","") + " id_" + d.i + "_" + d.j;
                })
                .text(function(d){return d.corr.toFixed(2);})
                .style("fill",function(d,i){return __colors(d.corr)});
            
            d3.select("text.colorbar.label").transition().duration(500).text("Pearson Correlation")
        }
    }
    
	//getter and setter functions
	__plot.width = function(w) {
		if(!arguments.length) return __width;
		__width = w;
        __width_scatter=__width;
		return __plot;
	}

	__plot.height = function(h) {
		if(!arguments.length) return __height;
		__height = h;
        __height_scatter=__height*3/6;
		return __plot;
	}
	
	__plot.margins = function(m) {
		if(!arguments.length) return __margins;
		__margins = m;
		return __plot;
	}

	__plot.colors = function(c) {
		if(!arguments.length) return __colors;
		__colors = c;
		return __plot;
	}

	__plot.axes_data = function(d) {
		if(!arguments.length) return __axes_data;
		__axes_data = d;
		return __plot;
	}
	
    __plot.data_matrix = function(d) {
		if(!arguments.length) return __data_matrix;
		__data_matrix = d;
		return __plot;
	}
    
    __plot.spear_matrix = function(d) {
		if(!arguments.length) return __spear_matrix;
		__spear_matrix = d;
		return __plot;
	}
    
    __plot.data_scatter = function(d) {
		if(!arguments.length) return __data_scatter;
		__data_scatter = d;
		return __plot;
	}
    
    __plot.data_venn = function(d) {
		if(!arguments.length) return __data_venn;
		__data_venn = d;
		return __plot;
	}
    
	__plot.container_corr = function(c) {
		if(!arguments.length) return __container;
		__container = c;
		return __plot;
	}
	
    __plot.container_scatter = function(c) {
		if(!arguments.length) return __container_scatter;
		__container_scatter = c;
		return __plot;
	}
    
    __plot.container_venn = function(c) {
		if(!arguments.length) return __container_venn;
		__container_venn = c;
		return __plot;
	}

	__plot.scale = function(s) {
		if(!arguments.length) return __scale;
		__scale = s;
		return __plot;
	}
	
	__plot.x_label = function(s) {
		if(!arguments.length) return __x_label;
		__x_label = s;
		return __plot;
	}
	
	__plot.y_label = function(s) {
		if(!arguments.length) return __y_label;
		__y_label = s;
		return __plot;
	}

	//return box plot object
	return __plot;
}
