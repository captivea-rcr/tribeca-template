odoo.define('survey_file_upload_field.form', function (require) {
'use strict';

require('web.dom_ready');
var publicWidget = require('web.public.widget');
var survey = require('survey.form');
var core = require('web.core');
var ajax = require('web.ajax');

var _t = core._t;

publicWidget.registry.SurveyFormWidget.include({

    _validateForm: function ($form, formData) {
        var self = this;
        var errors = {};
        var validationEmailMsg = _t("This answer must be an email address.");
        var validationDateMsg = _t("This is not a date");

        this._resetErrors();

        var data = {};
        formData.forEach(function (value, key) {
            data[key] = value;
        });

        var inactiveQuestionIds = this.options.sessionInProgress ? [] : this._getInactiveConditionalQuestionIds();

        $form.find('[data-question-type]').each(function () {
            var $input = $(this);
            var $questionWrapper = $input.closest(".js_question-wrapper");
            var questionId = $questionWrapper.attr('id');

            // If question is inactive, skip validation.
            if (inactiveQuestionIds.includes(parseInt(questionId))) {
                return;
            }

            var questionRequired = $questionWrapper.data('required');
            var constrErrorMsg = $questionWrapper.data('constrErrorMsg');
            var validationErrorMsg = $questionWrapper.data('validationErrorMsg');
            switch ($input.data('questionType')) {
                case 'char_box':
                    if (questionRequired && !$input.val()) {
                        errors[questionId] = constrErrorMsg;
                    } else if ($input.val() && $input.attr('type') === 'email' && !self._validateEmail($input.val())) {
                        errors[questionId] = validationEmailMsg;
                    } else {
                        var lengthMin = $input.data('validationLengthMin');
                        var lengthMax = $input.data('validationLengthMax');
                        var length = $input.val().length;
                        if (lengthMin && (lengthMin > length || length > lengthMax)) {
                            errors[questionId] = validationErrorMsg;
                        }
                    }
                    break;
                case 'numerical_box':
                    if (questionRequired && !data[questionId]) {
                        errors[questionId] = constrErrorMsg;
                    } else {
                        var floatMin = $input.data('validationFloatMin');
                        var floatMax = $input.data('validationFloatMax');
                        var value = parseFloat($input.val());
                        if (floatMin && (floatMin > value || value > floatMax)) {
                            errors[questionId] = validationErrorMsg;
                        }
                    }
                    break;
                case 'date':
                case 'datetime':
                    if (questionRequired && !data[questionId]) {
                        errors[questionId] = constrErrorMsg;
                    } else if (data[questionId]) {
                        var momentDate = moment($input.val());
                        if (!momentDate.isValid()) {
                            errors[questionId] = validationDateMsg;
                        } else {
                            var $dateDiv = $questionWrapper.find('.o_survey_form_date');
                            var maxDate = $dateDiv.data('maxdate');
                            var minDate = $dateDiv.data('mindate');
                            if ((maxDate && momentDate.isAfter(moment(maxDate)))
                                    || (minDate && momentDate.isBefore(moment(minDate)))) {
                                errors[questionId] = validationErrorMsg;
                            }
                        }
                    }
                    break;
                case 'simple_choice_radio':
                case 'multiple_choice':
                    if (questionRequired) {
                        var $textarea = $questionWrapper.find('textarea');
                        if (!data[questionId]) {
                            errors[questionId] = constrErrorMsg;
                        } else if (data[questionId] === '-1' && !$textarea.val()) {
                            // if other has been checked and value is null
                            errors[questionId] = constrErrorMsg;
                        }
                    }
                    break;
                case 'matrix':
                    if (questionRequired) {
                        var subQuestionsIds = $questionWrapper.find('table').data('subQuestions');
                        subQuestionsIds.forEach(function (id) {
                            if (!((questionId + '_' + id) in data)) {
                                errors[questionId] = constrErrorMsg;
                            }
                        });
                    }
                    break;
                case 'upload_file':
                    if (questionRequired && !$input.val()) {
                        errors[questionId] = constrErrorMsg;
                    }
                    break;
            }
        });
        if (_.keys(errors).length > 0) {
            this._showErrors(errors);
            return false;
        }
        return true;
    },

    _prepareSubmitValues: function (formData, params) {
        var self = this;
        formData.forEach(function (value, key) {
            switch (key) {
                case 'csrf_token':
                case 'token':
                case 'page_id':
                case 'question_id':
                    params[key] = value;
                    break;
            }
        });

        // Get all question answers by question type
        this.$('[data-question-type]').each(function () {
            switch ($(this).data('questionType')) {
                case 'text_box':
                case 'char_box':
                case 'numerical_box':
                    params[this.name] = this.value;
                    break;
                case 'date':
                    params = self._prepareSubmitDates(params, this.name, this.value, false);
                    break;
                case 'datetime':
                    params = self._prepareSubmitDates(params, this.name, this.value, true);
                    break;
                case 'simple_choice_radio':
                case 'multiple_choice':
                    params = self._prepareSubmitChoices(params, $(this), $(this).data('name'));
                    break;
                case 'matrix':
                    params = self._prepareSubmitAnswersMatrix(params, $(this));
                    break;
                case 'upload_file':
                    params = self._prepareDocuments(params, $(this));
                    break;
            }
        });
    },

    _prepareDocuments: function (params, $DocumentTable) {
        var self = this;
        var deferred = $.Deferred();
        var files = $DocumentTable[0].files;
        var file;
        var doc_list = []
        for (var i = 0; i < files.length; i++) {
            file = files[i];
            if (file !== null) {
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function(upload){
                    var data = upload.target.result;
                    doc_list.push(data.split(',')[1]);
                    params[$DocumentTable[0].name] = doc_list
                    ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                        model: 'survey.user_input',
                        method: 'search',
                        args: [[['access_token', '=', params['token']]]],
                        kwargs: {}
                    }).then(function(rec) {
                        var vals = {
                            'user_input_id': rec[0],
                            'question_id': parseInt($DocumentTable[0].name),
                        }
                        ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                            model: 'survey.user_input.line',
                            method: 'search',
                            args: [[['question_id', '=', parseInt($DocumentTable[0].name)],
                            ['user_input_id', '=', rec[0]]]],
                            kwargs: {}
                        }).then(function(line_rec) {
                            if (line_rec[0]){
                                var values = {
                                    'user_input_line_id': line_rec[0],
                                    'binary_filename' : file.name,
                                    'binary_data' : data.split(',')[1],
                                };
                                ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                                    model: 'survey.binary',
                                    method: 'create',
                                    args: [values],
                                    kwargs: {}
                                }).then(function(binary_rec) {
                                });
                            }else{
                                ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                                    model: 'survey.user_input.line',
                                    method: 'create',
                                    args: [vals],
                                    kwargs: {}
                                }).then(function(new_line) {
                                    var values = {
                                        'user_input_line_id': new_line,
                                        'binary_filename' : file.name,
                                        'binary_data' : data.split(',')[1],
                                    };
                                    ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                                        model: 'survey.binary',
                                        method: 'create',
                                        args: [values],
                                        kwargs: {}
                                    }).then(function(binary_rec) {
                                    });
                                })
                            }
                        });
                    });
                }
            }
        }
        return deferred.promise(params);
    },

});

});
