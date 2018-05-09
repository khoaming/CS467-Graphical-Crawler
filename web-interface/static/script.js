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
        console.log($("#options-form").serialize());
        $.post("process-options", $("#options-form").serialize(), function(data) {

        });
        $location.path( path );
        window.scrollTo(0,0);
    };
});
