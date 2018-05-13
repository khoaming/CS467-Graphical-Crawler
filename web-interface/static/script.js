//https://scotch.io/tutorials/single-page-apps-with-angularjs-routing-and-templating
var crawlerApp = angular.module('crawlerApp', ['ngRoute', 'ngAnimate']);

crawlerApp.config(function($routeProvider, $locationProvider) {
    $routeProvider
        .when('/', {
            templateUrl : 'form.html',
            controller : 'contentController'
        })
        .when('/results', {
            templateUrl : 'results.html',
            controller : 'contentController'
        });

        $locationProvider.html5Mode(true);
});

crawlerApp.controller('contentController', function($scope, $location) {
    $scope.$on('$routeChangeSuccess', function() {
    });
    $scope.go = function ( path ) {
        $('#submit-button').animate({
            'marginLeft': "70%",
        }, {duration: 600, queue:false});
        $.post("process-options", $("#options-form").serialize(), function(data) {

        });
        $location.path( path );
        window.scrollTo(0,0);
    };
});

crawlerApp.directive("graph", function() {
    return {
        link: function(scope, element, attrs) {
            initD3();
            //redraw the element when the window is resized?
            window.addEventListener("resize", function() {
                $("svg").remove();
                initD3();
            });
        }
    }
});

function initD3() {
    var random = Math.random();

    var zoom = d3.zoom()
        .on("zoom", zoomed);

    var svg = d3.select("#results-pane").append("svg")
        .attr("width", $("#results-pane").width())
        .attr("height", $("#results-pane").height());

    var width = svg.attr("width");
    var height = svg.attr("height");

    // add encompassing group for zooming
    var everything = svg.append("g")
        .attr("class", "everything");

    svg
        .call(zoom) // add zoom
        .call(zoom.transform, d3.zoomIdentity.translate(140, 120).scale(0.6)); // apply initial zoom

    var simulation = d3.forceSimulation()
        // pull nodes together based on the links between them
        .force("link", d3.forceLink().id(function(d) {return d.id;}).strength(0.3))
        // push nodes apart to space them out
        .force("charge", d3.forceManyBody().strength(-120))
        // add some collision detection so they don't overlap
        .force("collide", d3.forceCollide().radius(20))
        // and draw them around the centre of the space
        .force("center", d3.forceCenter(width / 2, height / 2));

    var tooltip = d3.select("body")
        .append("div")
        .attr('class', 'tooltip');

    d3.json("./static/data.json", function(error, graph) {
        if (error) throw error;

        var keyword_node = graph.keyword_node;

        var nodes = graph.nodes,
            nodeById = d3.map(nodes, function(d) {return d.id; }),
            links = graph.links,
            bilinks = [];

        links.forEach(function(link) {
            var s = nodeById.get(link.source),
                t = nodeById.get(link.target),
                i = {}; // intermediate node
            nodes.push(i);
            links.push({source: s, target: i}, {source: i, target: t});
            bilinks.push([s, i, t]);
        });

        var link = everything.selectAll(".link")
            .data(bilinks)
            .enter().append("path")
            .attr("class", "link")
            // random color based on depth
            .style("stroke", function(d) {return (d[0].id === 0) ? "black": "hsl(" + (360 * random + 90 * d[0].depth) + ",80%,50%)"});
            // pure random color
            // .style("stroke", function(d) {return (d[0].id === 0) ? "gray": "hsl(" + (360 * Math.random()) + ",80%,60%)"});
        var node = everything.selectAll(".node")
            .data(nodes.filter(function(d) {return d.depth; })) // to filter out intermediate nodes
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 8)
            // random color based on depth
            .attr("fill", function(d) { return (d.id === 0) ? "gray" : "hsl(" + (360 * random + 90 * d.depth) + ",80%,80%)"})
            // pure random color
            // .attr("fill", function(d) { return (d.id === 0) ? "gray" : "hsl(" + (360 * Math.random()) + ",80%,60%)"})
            .attr("stroke", function(d) {
                if (d.id === keyword_node) {
                    return "red";
                } else if (d.id === 0) {
                    return "black";
                } else {
                    return "hsl(" + (360 * random + 90 * d.depth) + ",80%,50%)";
                }})
            .attr("stroke-width", function(d) {return (d.id === keyword_node) ? "6px": "2px"})
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))

            .on("click", function(d) {
                tooltip.html('<a href="' + d.url + '">' + d.url + '</a>'); // show link
            })

            .on("dblclick", function(d) {
                location.href = d.url; // go to link
            })

            .on("mouseover", function(d) {
                d3.select(this).attr("r", 12);
                // d3.select(this).style('stroke', 'lightgreen');
                return tooltip.style("visibility", "visible").text(d.title);
            })

            // https://stackoverflow.com/questions/10805184/show-data-on-mouseover-of-circle
            .on("mousemove", function() {
                return tooltip.style("top", (event.pageY - 30) + "px")
                    .style("left", event.pageX + "px");
            })

            // hide tooltip on "mouseout"
            .on("mouseout", function(d) {
                d3.select(this).attr("r", 8);
                // d3.select(this).style('stroke', (d.id == 0) ? "red" : "silver");
                return tooltip.style("visibility", "hidden");
            });


        // node.append("title")
        //     .text(function(d) { return d.id; });

        simulation
            .nodes(nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(links);

        function ticked() {
            link.attr("d", positionLink);
            node.attr("transform", positionNode);
        }
    });


    function positionLink(d) {
        return "M " + d[0].x + "," + d[0].y
            + " S" + d[1].x + "," + d[1].y
            + " " + d[2].x + "," + d[2].y;
    }
    
    function positionNode(d) {
        return "translate(" + d.x + "," + d.y + ")";
    }
    
    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(d) {
        tooltip.style("visibility", "hidden"); // hide while dragging a node
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }
    
    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    function zoomed() {
        everything.attr("transform", d3.event.transform);
    }

}
