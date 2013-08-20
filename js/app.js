'use strict';

(function () {
    var GEO_API_URL = 'http://api.belowtheline.org.au/division';

    var geocoder = null;

    function divisionByLatLon(latitude, longitude) {
        $.ajax({
            type: "GET",
            url: GEO_API_URL + '?latitude=' + latitude + '&longitude=' + longitude
        }).done(function (data) {
            window.location = '/division/' + data.division + '.html';
        }).fail(function () {
             console.log("OH NOES");
        });
    }

    $(document).ready(function () {
        if (!!navigator.geolocation) {
            $(".geolocation-only").show();
            $(".geolocation-alt").hide();

            $('#geolocate').click(function (e) {
                e.preventDefault();
                $(this).button('loading');

                navigator.geolocation.getCurrentPosition(function (position) {
                    console.log(position.coords.latitude + ", " + position.coords.longitude);
                    divisionByLatLon(position.coords.latitude,
                                     position.coords.longitude);
                }, function (error) {
                    console.log(error);
                });
            });
        }

        $('#address').submit(function (e) {
            e.preventDefault();
            $('#addressSearch').button('loading');

            var address = $('#addressInput').val();

            if (geocoder == null) {
                geocoder = new google.maps.Geocoder();
            }

            geocoder.geocode({ address: address, region: 'au'},
                function (results, status) {
                    var latlng = results[0].geometry.location;
                    divisionByLatLon(latlng.lat(), latlng.lng());
                });
        });

        $('#division').submit(function (e) {
            e.preventDefault();

            var divisionId = $('#divisionSelector').val();
            window.location = '/division/' + divisionId + '.html';
        })
    });
}());


angular.module('belowtheline', ['ui.sortable']);

function BallotPickerCtrl($scope, $http, $location, $window) {

    var divisionPath = $location.path();
    var division = {};
    var state = {};

    $scope.divisionCandidates = [];
    $scope.divisionBallotOrder = [];
    $scope.stateCandidates = [];
    $scope.stateBallotOrder = [];
    $scope.parties = {};

    $scope.groups = [];
    $scope.groupBallotOrder = [];

    $scope.orderByGroup = true;

    var applyGroupOrdering = function() {
        $scope.stateCandidates = _.sortBy($scope.stateCandidates, function(candidate) {
            return _.indexOf($scope.groups, state.groups[candidate.group]);
        });
    };

    $scope.showOrderByCandidate = function() {
        applyGroupOrdering();
        $scope.orderByGroup = false;
    };

    $scope.showOrderByGroup = function() {
        if(
            !$scope.stateDirty() ||
            $window.confirm("Are you sure? You'll lose any changes you made to candidate ordering.")
        ) {
            $scope.resetState();
            $scope.orderByGroup = true;
        }
    };

    $scope.groupsDirty = function() {
        return !(_.isEqual($scope.groups, $scope.groupBallotOrder));
    };

    $scope.stateDirty = function() {
        return !(_.isEqual($scope.stateCandidates, $scope.stateBallotOrder));
    };

    $scope.divisionDirty = function() {
        return !(_.isEqual($scope.divisionCandidates, $scope.divisionBallotOrder));
    };

    $scope.resetGroups = function() {
        $scope.groups = $scope.groupBallotOrder.slice();
    };
    $scope.resetState = function() {
        $scope.stateCandidates = $scope.stateBallotOrder.slice();
    };
    $scope.resetDivision = function() {
        $scope.divisionCandidates = $scope.divisionBallotOrder.slice();
    };

    $scope.downloadPDF = function () {
        console.log("Here we go!");
        if ($scope.orderByGroup) {
          applyGroupOrdering();
        }

        console.log($scope.divisionCandidates);
        console.log($scope.stateCandidates);
        console.log($scope.groups);

        function makeTicket(order, ballotOrder) {
            var ticket = [];

            angular.forEach(ballotOrder, function (candidate, idx) {
                ticket.push(_.indexOf(order, candidate) + 1);
            });

            return ticket;
        }

        var division_ticket = makeTicket($scope.divisionCandidates,
                                         $scope.divisionBallotOrder);
        var senate_ticket = makeTicket($scope.stateCandidates,
                                       $scope.stateBallotOrder);

        console.log(division_ticket);
        console.log(senate_ticket);

        function make_input(name, value) {
            return '<input type="hidden" name="' + name + '" value="' + value + '"/>';
        }

        var form = '<form action="http://api.belowtheline.org.au/pdf" method="POST">' +
                    make_input('division', divisionPath.slice(1)) +
                    make_input('state', division.division.state.split('/')[1]) +
                    make_input('division_ticket', division_ticket.join(',')) +
                    make_input('senate_ticket', senate_ticket.join(',')) +
                    '</form>';
        $(form).appendTo('body').submit().remove();
    }

    $http.get('/division' + divisionPath + '.json').success(function(data) {
        division = data;
        $scope.divisionName = data.division.name
        $scope.divisionCandidates = data.candidates;
        $scope.divisionBallotOrder = data.candidates.slice();

        $http.get(division.division.state + '.json').success(function(data) {
            state = data;
            $scope.stateCandidates = _.map(data.ballot_order, function(id) {
                return data.candidates[id];
            });
            $scope.stateBallotOrder = $scope.stateCandidates.slice();

            var groupNames = _.without(_.uniq(_.pluck($scope.stateCandidates, 'group')), 'UG');
            var ungroupedCandidates = _.where($scope.stateCandidates, { group: 'UG' });
            $scope.groups = _.map(groupNames, function(name) { return state.groups[name]; });
            angular.forEach(ungroupedCandidates, function(candidate, idx) {
              var newGroup = {
                name: candidate.first_name + ' ' + candidate.last_name,
              };
              if(candidate.party) {
                newGroup.parties = [ candidate.party ];
              }

              var newGroupName = 'UG' + (idx + 1);
              state.groups[newGroupName] = newGroup;
              $scope.groups = $scope.groups.concat(newGroup);
              candidate.group = newGroupName;
            });
            $scope.groupBallotOrder = $scope.groups.slice();

        });
    });

    $http.get('/parties.json').success(function(data) {
        $scope.parties = data;
    });

}

function TicketViewerCtrl($scope, $http, $location) {
    var state = $location.path();

    $scope.ticket = [null, null];
    $scope.candidateOrder = [[], []];

    $scope.ticketList = [];

    $scope.changeTicket = function (idx) {
        if (!$scope.ticket[idx]) {
            $scope.candidateOrder[idx] = $scope.ballotOrder;
            return;
        }

        var data = $scope.ticket[idx].split('-');
        var group = data[0];
        var ticket = parseInt(data[1]) - 1;

        $scope.candidateOrder[idx] = $scope.groups[group].tickets[ticket];
    }

    function generateTicketList() {
        var groups = []
        var tickets = [];

        angular.forEach($scope.groups, function (group, group_id) {
            groups.push(group_id);
        });

        groups.sort(function (a, b) {
            if (a.length != b.length) {
                return a.length - b.length;
            } else if (a < b) {
                return -1
            } else if (b > a) {
                return 1;
            } else {
                return 0;
            }
        })

        angular.forEach(groups, function (group_id, idx) {
            var group = $scope.groups[group_id];

            if (group.tickets.length == 1) {
                tickets.push({
                    id: "" + group_id + "-1",
                    name: group.name
                });
            } else {
                angular.forEach(group.tickets, function (ticket, idx) {
                    tickets.push({
                        id: "" + group_id + "-" + (idx + 1),
                        name: group.name + " (" + (idx + 1) + " of " + group.tickets.length + ")"
                    });
                });
            }
        });

        $scope.ticketList = tickets;
    }

    $http.get('/state' + state + '.json').
        success(function (data) {
            $scope.state = data.state;
            $scope.stateOrTerritory = data.state_or_territory;
            $scope.candidates = data.candidates;
            $scope.ballotOrder = data.ballot_order;
            $scope.groups = data.groups;

            $scope.candidateOrder = [$scope.ballotOrder, $scope.ballotOrder];

            generateTicketList();
        }).
        error(function () {
            console.log("I have no idea");
        });
    $http.get('/parties.json').
        success(function (data) {
            $scope.parties = data;
        }).
        error(function () {
            console.log("I have no idea");
        });
}
