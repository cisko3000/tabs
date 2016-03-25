$(function(){
	var delay_func = (function(){
  		var timer = 0;
  		return function(callback, ms){
    		clearTimeout (timer);
    		timer = setTimeout(callback, ms);
  			};
	}) ();
	function alphaSort(dtype) {
		return function(left, right) {
			if (!left[dtype]()) return 1;
			else if (!right[dtype]()) return 0;
			return left[dtype]().toLowerCase() == right[dtype]().toLowerCase() ? 0 : (left[dtype]().toLowerCase() < right[dtype]().toLowerCase() ? -1: 1);
		};
	}
	// Constructors
	var Contact = function(name,id) {
			this.name = name;
			this.id = id;
		}
	//$SCRIPT_ROOT+"/somepath";
	var request = {
		url : '',
		type: '',
		contentType: "application/json",
		accepts: "application/json",
		cache: false,
		dataType: 'json',
		data: ''
	};
	var search_request = {
		url : '',
		type: '',
		//contentType: "application/json",
		accepts: "application/json",
		cache: false,
		dataType: 'json',
		data: ''
	};
	function ContactsViewModel() {
		var self = this;
		self.contactsURI = $SCRIPT_ROOT+'/api/contacts';
		self.contactURI = $SCRIPT_ROOT+'/api/contact/';
		self.contacts = ko.observableArray();
		self.sortedBy = '';
		//self.magnified = ko.observable('magnified');
		//self.notesSpan50 = ko.observable('notes-span-50');
		self.magnify = function(contact, event) {
			//console.log(contact);
			//console.log($(event.target).html());
			contact.emailDisplay(ko.observable('magnified'));
			contact.notesDisplay(ko.observable('magnified'));
			//if ($(event.target).attr('data-type','') == 'email') {contact.emailDisplay('magnified');}
			//else if ($(event.target).attr('data-type','') == 'notes') {contact.notesDisplay('magnified');}
		}
		self.magnifyReset = function(contact, event) {
			//console.log(contact);
			contact.emailDisplay('notes-span-50');
			contact.notesDisplay('notes-span-100');
			//if ($(event.target).attr('data-type','') == 'email') {contact.emailDisplay('notes-span-50');}
			//else if ($(event.target).attr('data-type','') == 'notes') {contact.notesDisplay('notes-span-100');}
		}

		self.ajax = function(uri, method, data) {
			var localRequest = request;
			localRequest.url = uri;
			localRequest.method = method;
			localRequest.data = JSON.stringify(data);
				/*,
				beforeSend: function (xhr) {
					xhr.setRequestHeader("Authorization", "Basic " + btoa(self.username+":" + self.password));
				}
				error: function(jqXHR) {
					console.log("ajax error " + jqXHR.status);
				}*/
			return $.ajax(localRequest);
		}
		self.ajax_search = function (uri, method, data) {
			var localRequest = search_request;
			localRequest.url = uri;
			localRequest.method = method;
			localRequest.data = data;
			console.log('localRequest.data');
			console.log(localRequest.data);
			return $.ajax(localRequest);
		}
		self.beginAddContact = function(contact) {
			$('#addContact').modal('show');
		}
		self.beginEdit = function(contact) {
			editContactViewModel.setContact(contact);
			$('#edit').modal('show');
		}
		self.edit = function(contact, data) {
			self.ajax(self.contactURI+contact.id(), 'PUT', data).done(function(res) {
				self.updateContact(contact, res);
			});
		}
		self.updateContact = function(contact, newContact) {
			var i = self.contacts.indexOf(contact);
			self.contacts()[i].name(newContact.name);
			self.contacts()[i].email(newContact.email);
			self.contacts()[i].notes(newContact.notes);
			self.contacts()[i].id(newContact.id);
		}

		self.ajax(self.contactsURI, 'GET').done(function(data) {
			//addProjectViewModel.availableContacts.removeAll();
			for (var i = 0; i < data.length; i++) {
				self.contacts.push({
					name: 	ko.observable(data[i].name),
					email: 	ko.observable(data[i].email),
					notes: 	ko.observable(data[i].notes),
					id: 	ko.observable(data[i].id),
					emailDisplay : ko.observable('notes-span-50'),
					notesDisplay : ko.observable('notes-span-100')
				});
				addProjectViewModel.availableContacts.push(new Contact(data[i].name,data[i].id));
			}
		});
		self.search_for = function(the_term) {
			var data = {sstr:the_term};
			console.log(data);
			self.ajax_search(self.contactsURI, 'GET' ,data).done(function(data) {
				self.contacts.removeAll();
				for (var i = 0; i < data.length; i++) {
					self.contacts.push({
						name: 	ko.observable(data[i].name),
						email: 	ko.observable(data[i].email),
						notes: 	ko.observable(data[i].notes),
						id: 	ko.observable(data[i].id)
					});
				}
			});
		}
		self.add = function(contact) {
			self.ajax(self.contactsURI, 'POST', contact).done(function (data) {
				self.contacts.push({
					name: ko.observable(data.name),
					email: ko.observable(data.email),
					notes: ko.observable(data.notes),
					id: ko.observable(data.id)
				});
				addProjectViewModel.availableContacts.push(new Contact(data.name,data.id));
			});
		}
		self.remove = function(contact) {
			self.ajax(self.contactURI+contact.id(), 'DELETE' ).done(function() {
				self.contacts.remove(contact);
			});
		}

		self.sortContacts = function(column) {
			self.contacts.sort(alphaSort(column));
			self.sortedBy = self.sortedBy == '' ? column : '';
			if (self.sortedBy == '') self.contacts.reverse();

		}
		
	}
	function ProjectsViewModel() {
		var self = this;
		self.projectsURI = $SCRIPT_ROOT+'/api/projects';
		self.projectURI = $SCRIPT_ROOT+'/api/project/';
		self.projects = ko.observableArray();
		self.ajax = function(uri, method, data) {
			var localRequest = request;
			localRequest.url = uri;
			localRequest.method = method;
			localRequest.data = JSON.stringify(data);
			return $.ajax(localRequest);
		}
		self.ajax_search = function (uri, method, data) {
			var localRequest = search_request;
			localRequest.url = uri;
			localRequest.method = method;
			localRequest.data = data;
			return $.ajax(localRequest);
		}
		self.beginAddProject = function(project) {
			//addProjectViewModel.availableContacts(addProjectViewModel.availableContacts);
			$('#addProject').modal('show');
			$('#addProject').find('select').select2({width: '100%'});
		}
		self.add = function(project) {
			self.ajax(self.projectsURI, 'POST', project).done(function (data) {
				console.log(data);
				self.projects.push({
					contact_id: ko.observable(data.contact_id),
					contact: ko.observable(data.contact),
					name: ko.observable(data.name),
					notes: ko.observable(data.notes),
					id: ko.observable(data.id),
					total: 	ko.observable(111)
				});
			});
		}
		self.beginEdit = function(project) {
			editProjectViewModel.setProject(project);
			$('#editProject').modal('show');
		}
		self.edit = function(project, data) {
			self.ajax(self.projectURI+project.id(),'PUT',data).done(function(res) {
				self.updateProject(project, res);
			});
		}
		self.remove = function(project) {
			self.ajax(self.projectURI+project.id(), 'DELETE' ).done(function() {
				self.projects.remove(project);
			});
		}
		self.updateProject = function(project, newProject) {
			var i = self.projects.indexOf(project);
			self.projects()[i].contact(newProject.contact);
			self.projects()[i].name(newProject.name);
			self.projects()[i].notes(newProject.notes);
			console.log(self.projects()[i]);
		}
		self.ajax(self.projectsURI, 'GET').done(function(data) {
			for (var i = 0; i < data.length; i++) {
				self.projects.push({
					contact: 	ko.observable(data[i].contact),
					contact_id: 	ko.observable(data[i].contact_id),
					name: 	ko.observable(data[i].name),
					notes: 	ko.observable(data[i].notes),
					total: 	ko.observable(77),
					id: 	ko.observable(data[i].id)
				});
			}	
		});
		self.search_for = function(the_term) {
			var data = {sstr:the_term};
			console.log(data);
			self.ajax_search(self.projectsURI, 'GET' ,data).done(function(data) {
				self.projects.removeAll();
				for (var i = 0; i < data.length; i++) {
					self.projects.push({
						contact: 	ko.observable(data[i].contact),
						contact_id: 	ko.observable(data[i].contact_id),
						name: 	ko.observable(data[i].name),
						notes: 	ko.observable(data[i].notes),
						total: 	ko.observable(77),
						id: 	ko.observable(data[i].id)
					});
				}
			});
		}
		self.sortProjects = function(column) {
			self.projects.sort(alphaSort(column));
			self.sortedBy = self.sortedBy == '' ? column : '';
			if (self.sortedBy == '') self.projects.reverse();

		}
	}
	function AddProjectViewModel() {
		var self = this;
		//self.availableContacts = ko.observableArray();
		self.availableContacts = ko.observableArray();
		self.contact = ko.observable();
		self.name = ko.observable();
		self.notes = ko.observable();
		self.total = ko.observable();

		self.addProject = function() {
			$('#addProject').modal('hide');
			$('#addProject').find('select').select2('destroy');
			// When addContact is executed, add details to contacts list
			// then reset the dialog values to empty strings.
			console.log(self.contact());
			projectsViewModel.add({
				project_name: self.name(),
				project_contact: self.contact(),
				project_notes: self.notes()

			});
			self.name('');
			self.contact('');
			self.notes('');
		}
	}
	function EditProjectViewModel() {
		var self = this;
		self.availableContacts = ko.observableArray();
		//self.contact = ko.observable();
		self.contact_id = ko.observable();
		self.name = ko.observable();
		self.notes = ko.observable();
		self.id = ko.observable();
		// When setContact is called, init self fields and show edit button modal
		self.setProject = function(project) {
			self.project = project;
			self.availableContacts = addProjectViewModel.availableContacts;
			//self.contact(project.contact_id());
			self.contact_id(project.contact_id());
			self.name(project.name());
			self.notes(project.notes());
			self.id(project.id());
			$('#editProject').modal('show'); 
		}
		self.editProject = function() {
			$('#editProject').modal('hide');
			projectsViewModel.edit(self.project, {
				project_contact_id: self.contact_id(),
				project_name: self.name(),
				project_notes:self.notes(),
				project_id: self.id()
			});
		}

		//contact_id: ko.observable(data.contact_id),
		//contact: ko.observable(data.contact),
		//name: ko.observable(data.name),
		//notes: ko.observable(data.notes),
		//id: ko.observable(data.id),
		//total: 	ko.observable(111)
	}
	function AddContactViewModel() {
		var self = this;
		self.name = ko.observable();
		self.email = ko.observable();
		self.notes = ko.observable();

		self.addContact = function() {
			$('#addContact').modal('hide');
			// When addContact is executed, add details to contacts list
			// then reset the dialog values to empty strings.
			contactsViewModel.add({
				contact_name: self.name(),
				contact_email: self.email(),
				contact_notes: self.notes()

			});
			self.name('');
			self.email('');
			self.notes('');
		}
	}
	function EditContactViewModel() {
		var self = this;
		self.name = ko.observable();
		self.email = ko.observable();
		self.notes = ko.observable();
		self.id = ko.observable();

		// When setContact is called, init self fields and show edit button modal
		self.setContact = function(contact) {
			self.contact = contact;
			self.name(contact.name());
			self.email(contact.email());
			self.notes(contact.notes());
			self.id(contact.id());
			$('#editContact').modal('show'); 
		}
		self.editContact = function() {
			$('#editContact').modal('hide');
			contactsViewModel.edit(self.contact, {
				contact_name: self.name(),
				contact_email:self.email(),
				contact_notes:self.notes(),
				contact_id: self.id()
			});
		}
	}

	function EntriesViewModel() {
		var self = this;
		self.entriesURI = $SCRIPT_ROOT+'/api/entries';
		self.entryURI = $SCRIPT_ROOT+'/api/entry/';
		self.entries = ko.observableArray();
		self.entries_total = ko.observable();
		self.sortedBy = '';
		self.ajax = function(uri, method, data) {
			var localRequest = request;
			localRequest.url = uri;
			localRequest.method = method;
			localRequest.data = JSON.stringify(data);
			return $.ajax(localRequest);
		}
		self.ajax(self.entriesURI, 'GET').done(function(data) {
			for (var i = 0; i < data[0].entries.length; i++) {
				var dtemp = data[0].entries[i];
				self.entries.push({
					project_name: 	ko.observable(dtemp.project_name),
					start: 	ko.observable(dtemp.start),
					stop: 	ko.observable(dtemp.stop),
					delta: 	ko.observable(dtemp.delta)
				});
			}
			self.entries_total(data[0].entries_total);
		});
		function alphaSort(dtype) {
			return function(left, right) {
				return left[dtype]().toLowerCase() == right[dtype]().toLowerCase() ? 0 : (left[dtype]().toLowerCase() < right[dtype]().toLowerCase() ? -1 : 1);
			};
		}
		function numSort(dtype) {
			return function(left, right) {
				return parseFloat(left[dtype]()) == parseFloat(right[dtype]()) ? 0 : (parseFloat(left[dtype]()) < parseFloat(right[dtype]()) ? -1 : 1);
			};
		}
		self.sortEntriesProjectName = function() {
			self.entries.sort(alphaSort('project_name'));
			self.sortedBy = self.sortedBy == '' ? 'project_name' : '';
			if (self.sortedBy == '') self.entries.reverse();
		}
		self.sortEntriesStart = function() {
			self.entries.sort(alphaSort('start'));
			self.sortedBy = self.sortedBy == '' ? 'start' : '';
			if (self.sortedBy == '') self.entries.reverse();
		}
		self.sortEntriesDuration = function() {
			self.entries.sort(numSort('delta'));
			self.sortedBy = self.sortedBy == '' ? 'delta' : '';
			if (self.sortedBy == '') self.entries.reverse();
		}
		self.ajax_search = function (uri, method, data) {
			var localRequest = search_request;
			localRequest.url = uri;
			localRequest.method = method;
			localRequest.data = data;
			return $.ajax(localRequest);
		}
		self.search_for = function(the_term) {
			var data = {sstr:the_term};
			console.log(data);
			self.ajax_search(self.entriesURI, 'GET' ,data).done(function(data) {
				self.entries.removeAll();
				for (var i = 0; i < data[0].entries.length; i++) {
					var dtemp = data[0].entries[i];
					self.entries.push({
						project_name: 	ko.observable(dtemp.project_name),
						start: 	ko.observable(dtemp.start),
						stop: 	ko.observable(dtemp.stop),
						delta: 	ko.observable(dtemp.delta)
					});
				}
				self.entries_total(data[0].entries_total);
			});
		}
	}
	// Contacts
	var contactsViewModel = new ContactsViewModel();
	var addContactViewModel = new AddContactViewModel();
	var editContactViewModel = new EditContactViewModel();
	ko.applyBindings(contactsViewModel, $('#contacts_container')[0]);
	ko.applyBindings(addContactViewModel, $('#addContact')[0]);
	ko.applyBindings(editContactViewModel, $('#editContact')[0]);

	// Projects
	var projectsViewModel = new ProjectsViewModel();
	var addProjectViewModel = new AddProjectViewModel();
	var editProjectViewModel = new EditProjectViewModel();
	ko.applyBindings(projectsViewModel, $('#projects_container')[0]);
	ko.applyBindings(addProjectViewModel, $('#addProject')[0]);
	ko.applyBindings(editProjectViewModel, $('#editProject')[0]);

	// TimeEntry
	var entriesViewModel = new EntriesViewModel();
	ko.applyBindings(entriesViewModel, $('#entries_container')[0]);

	var system_search = function() {
		var term = $('input[name="sstr"]').val();
		contactsViewModel.search_for(term);
		projectsViewModel.search_for(term);
		entriesViewModel.search_for(term);
	}
	$('input[name="sstr"]').bind('keyup', function(){
		delay_func(system_search,300);});
});