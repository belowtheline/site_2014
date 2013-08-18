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
    $scope.partyBallotOrder = [];

    $scope.orderByParty = true;

    $scope.showOrderByCandidate = function() {
        $scope.orderByParty = false;
    };

    $scope.skipToOrderByCandidate = function() {
        if(
            !$scope.partiesOrderDirty() ||
            $window.confirm("Are you sure? You'll lose the changes you made to party ordering.")
        ) {
            $scope.orderByParty = false;
        }
    };

    $scope.showOrderByParty = function() {
        if(
            (!$scope.stateDirty() && !$scope.divisionDirty()) ||
            $window.confirm("Are you sure? You'll lose the changes you made to candidate ordering.")
        ) {
            $scope.orderByParty = true;
        }
    };

    $scope.partiesOrderDirty = function() {
        return !(_.isEqual($scope.orderedParties, $scope.orderedPartiesOriginal));
    };

    $scope.stateDirty = function() {
        return !(_.isEqual($scope.stateCandidates, $scope.stateBallotOrder));
    };

    $scope.divisionDirty = function() {
        return !(_.isEqual($scope.divisionCandidates, $scope.divisionBallotOrder));
    };

    $scope.resetParties = function() {
        $scope.orderedParties = $scope.orderedPartiesOriginal.slice();
    };
    $scope.resetState = function() {
        $scope.stateCandidates = $scope.stateBallotOrder.slice();
    };
    $scope.resetDivision = function() {
        $scope.divisionCandidates = $scope.divisionBallotOrder.slice();
    };


    $http.get('/division' + divisionPath + '.json').success(function(data) {
        division = data;
        $scope.divisionCandidates = data.candidates;
        $scope.divisionBallotOrder = data.candidates.slice();
        $http.get(division.division.state + '.json').success(function(data) {
            state = data;
            $scope.stateCandidates = _.map(data.ballot_order, function(id) {
                return data.candidates[id];
            });
            $scope.stateBallotOrder = $scope.stateCandidates.slice();
            $http.get('/parties.json').success(function(data) {
                var partyCodes = _.filter(_.keys(data), function(partyCode) {
                    var inDivision = _.findWhere($scope.divisionCandidates, {party: partyCode});
                    var inState = _.findWhere($scope.stateCandidates, {party: partyCode});
                    return(inDivision || inState);
                });
                $scope.parties = _.pick(data, partyCodes);
                $scope.orderedParties = _.values($scope.parties); // XXX, Use ballot order? Alphabetical?
                $scope.orderedPartiesOriginal = $scope.orderedParties.slice();
            });
        });
    });

}

function TicketViewerCtrl($scope, $http, $location) {
    var state = $location.path();

    $scope.ticket = [null, null];
    $scope.candidateOrder = [[], []];

    $scope.ticketList = [];

    $scope.changeTicket = function (idx) {
        console.log(">>> " + $scope.ticket[idx]);

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
        var tickets = [];

        angular.forEach($scope.groups, function (group, group_id) {
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
            console.log(data);
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
