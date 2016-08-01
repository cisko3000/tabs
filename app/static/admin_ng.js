var app = angular.module("tabsData", ['ui.bootstrap']);
app.service('ContactsService', function($http) {
	this.value = function() {return $http.get($SCRIPT_ROOT+'api/contacts')};
});
app.service('ProjectsService', function($http) {
	this.value = function() {return $http.get($SCRIPT_ROOT+'api/projects')};
});
app.controller("myContacts", function($scope, $http,  $modal, ContactsService) {
	ContactsService.value().then(function(response) {
		$scope.contacts = response.data;
	});
	ContactsService.update = function() {
		ContactsService.value().then(function(response) {
			$scope.contacts = response.data;
		});
	}
	$scope.deleteContact = function(contact) {
		$http.delete($SCRIPT_ROOT+'api/contact/'+contact.id).then(function() {
			ContactsService.value().then(function(response) {
				$scope.contacts = response.data;
			});
		});
	}
	// Sorting
	$scope.propertyName = 'name';
	$scope.reverse = true;
	$scope.sortBy = function(propertyName) {
		$scope.reverse = ($scope.propertyName === propertyName) ? !$scope.reverse : false;
		$scope.propertyName = propertyName;
	};
	// Modal
	$scope.modalInstance;
	$scope.contactAddBegin = function() {
		$scope.modalInstance = $modal.open({
			templateUrl: 'addContact.html'+'?bust=' + Math.random().toString(36).slice(2),
			controller : 'addContactController',
			scope : $scope
		});
	};
	$scope.contactEditBegin = function(contact) {
		$scope.modalInstance = $modal.open({
			templateUrl: 'addContact.html'+'?bust=' + Math.random().toString(36).slice(2),
			controller : 'editContactController',
			scope : $scope,
			resolve: {
				contact : function() {return contact;},
			}
		});
	};
});
app.controller("editContactController", function($scope, $http, ContactsService, contact) {
	$scope.contact = contact;
	$scope.data = {
		cname  : contact.name,
		cemail : contact.email,
		cnotes : contact.notes,
		confirmLabel : 'Save',
	};
	$scope.cancel = function () {
    	$scope.modalInstance.dismiss('cancel');
	};
	$scope.addContact = function() {
		if ($scope.data.cname == '' || $scope.data.cemail == '') {
			alert('Name and Email required');
			return;
		}
		else {
			var newData = {
				contact_name :$scope.data.cname,
				contact_email:$scope.data.cemail,
				contact_notes:$scope.data.cnotes,
			}
			$http.put($SCRIPT_ROOT+'api/contact/'+$scope.contact.id, newData).then(function (response) {
				ContactsService.update();
				$scope.modalInstance.dismiss('cancel');
			});
		}
	}
});
app.controller("addContactController", function($scope, $http, ContactsService) {
	$scope.data = {
		confirmLabel : 'Create Contact',
		cname  : '',
		cemail : '',
		cnotes : '',
	};
	$scope.cancel = function () {
    	$scope.modalInstance.dismiss('cancel');
	};
	$scope.addContact = function() {
		if ($scope.data.cname == '' || $scope.data.cemail == '') {
			alert('Name and Email required');
			return;
		}
		else {
			var newData = {
				contact_name :$scope.data.cname,
				contact_email:$scope.data.cemail,
				contact_notes:$scope.data.cnotes,
			}
			$http.post($SCRIPT_ROOT+'api/contacts',newData).then(function (response) {
				ContactsService.update();
				$scope.modalInstance.dismiss('cancel');
			});
		}
	}
});
app.controller("myProjects", function($scope, $http, $modal, ProjectsService) {
	ProjectsService.value().then(function(response) {
		$scope.projects = response.data;
	})
	ProjectsService.update = function() {
		ProjectsService.value().then(function(response) {
			$scope.projects = response.data;
		});
	}
	$scope.deleteProject = function(project) {
		$http.delete($SCRIPT_ROOT+'api/project/'+project.id).then(function() {
			ProjectsService.value().then(function(response) {
				$scope.projects = response.data;
			});
		});
	}
	// Sorting
	$scope.propertyName = 'contact';
	$scope.reverse = true;
	$scope.sortBy = function(propertyName) {
		$scope.reverse = ($scope.propertyName === propertyName) ? !$scope.reverse : false;
		$scope.propertyName = propertyName;
	};
	$scope.modalInstance;
	$scope.projectAddBegin = function() {
		$scope.modalInstance = $modal.open({
			templateUrl: 'addProject.html'+'?bust=' + Math.random().toString(36).slice(2),
			controller : 'addProjectController',
			scope : $scope
		});
	};
	$scope.projectEditBegin = function(project) {
		$scope.modalInstance = $modal.open({
			templateUrl: 'addProject.html'+'?bust=' + Math.random().toString(36).slice(2),
			controller : 'editProjectController',
			scope : $scope,
			resolve: {
				project : function() {return project;},
			}
		});
	};
});
app.controller("editProjectController", function($scope, $http, ProjectsService, ContactsService, project) {
	$scope.project = project;
	$scope.data = {
		project_name : project.name,
		project_notes : project.notes,
		confirmLabel : 'Save Project',
	};
	ContactsService.value().then(function(response) {
		$scope.data.contactsList = response.data;
		$scope.data.selected = $scope.data.contactsList.filter(function(cv) {
			return ($scope.project.contact_id == cv.id );
		})[0];
	});
	$scope.cancel = function () {
    	$scope.modalInstance.dismiss('cancel');
	};
	$scope.addProject = function() {
		if ($scope.data.contactsList == '' ) {
			alert('Name and Email required');
			return;
		}
		else {
			var newData = {
				project_contact_id: $scope.data.selected.id, // contact.id
				project_name: $scope.data.project_name,
				project_notes: $scope.data.project_notes,
			};
			$http.put($SCRIPT_ROOT+'api/project/'+$scope.project.id ,newData).then(function (response) {
				ProjectsService.update();
				$scope.modalInstance.dismiss('cancel');
			});
		}
	}
});
app.controller("addProjectController", function($scope, $http, ProjectsService, ContactsService) {
	$scope.data = {
		project_name : '',
		project_notes : '',
		confirmLabel : 'Create Project',
	};
	ContactsService.value().then(function(response) {$scope.data.contactsList = response.data;});
	$scope.cancel = function () {
    	$scope.modalInstance.dismiss('cancel');
	};
	$scope.addProject = function() {
		if ($scope.data.contactsList == '' ) {
			alert('Name and Email required');
			return;
		}
		else {
			var newData = {
				project_contact_id: $scope.data.selected.id, // contact.id
				project_name: $scope.data.project_name,
				project_notes: $scope.data.project_notes,
			};
			$http.post($SCRIPT_ROOT+'api/projects',newData).then(function (response) {
				ProjectsService.update();
				$scope.modalInstance.dismiss('cancel');
			});
		}
	}
});
app.controller("myEntries", function($scope, $http) {
	$http.get($SCRIPT_ROOT+'api/entries').then(function (response) {
		$scope.entries = response.data[0].entries;
		$scope.total = response.data[0].entries_total;
	});
	// Sorting
	$scope.propertyName = 'project_name';
	$scope.reverse = false;
	$scope.sortBy = function(propertyName) {
		$scope.reverse = ($scope.propertyName === propertyName) ? !$scope.reverse : false;
		$scope.propertyName = propertyName;
	};
});