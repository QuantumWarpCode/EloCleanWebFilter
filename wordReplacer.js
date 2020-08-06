// ==UserScript==
// @name         E'lo Clean Web Filter Word Replacer
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Replaces naughty words to make them more friendly
// @author       QuantumWarpCode
// @match        http://*/*
// @match        https://*/*
// @grant        none
// ==/UserScript==

(function() {
    var words = {
    ///////////////////////////////////////////////////////


        // Syntax: 'Search word' : 'Replace word',
        '/\\b(ass)\\b/g' : 'a**',
        '/\\b(Ass)\\b/g' : 'A**',
        '/\\b(asses)\\b/g' : 'a**es',
        '/\\b(Asses)\\b/g' : 'A**es'


    ///////////////////////////////////////////////////////
    };

    var regexs = [], replacements = [], word, userRegexp;
    var rIsRegexp = /^\/(.+)\/([gim]+)?$/;
    var tagsWhitelist = ['PRE', 'BLOCKQUOTE', 'CODE', 'INPUT', 'BUTTON', 'TEXTAREA', 'TITLE'];

    function prepareRegex(string) {
        return string.replace(/([\[\]\^\&\$\.\(\)\?\/\\\+\{\}\|])/g, '\\$1');
    }

    function isTagOk(tag) {
        return tagsWhitelist.indexOf(tag) === -1;
    }

    for (word in words) {
        if ( typeof word === 'string' && words.hasOwnProperty(word) ) {
            userRegexp = word.match(rIsRegexp);

            // add the search/needle/query
            if (userRegexp) {
                regexs.push(
                    new RegExp(userRegexp[1], 'g')
                );
            } else {
                regexs.push(
                    new RegExp(prepareRegex(word).replace(/\\?\*/g, function (fullMatch) {
                        return fullMatch === '\\*' ? '*' : '[^ ]*';
                    }), 'g')
                );
            }

            // add the replacement
            replacements.push( words[word] );
        }
    }

    var texts, text, i
    texts = document.evaluate('//text()[ normalize-space(.) != "" ]', document, null, 6, null);
    for (i = 0; text = texts.snapshotItem(i); i += 1) {
        if ( isTagOk(text.parentNode.tagName) ) {
            if (text.data != null){
                regexs.forEach(function (value, index) {
                    text.data = text.data.replace(value, replacements[index]);
                });
                //text.data = text.data.replace(/\b(Ass)\b/g, 'A**');
                //text.data = text.data.replace(/\b(ass)\b/g, 'a**');
            }
        }
    }
    regexs.forEach(function (value, index) {
        document.title = document.title.replace(value, replacements[index]);
    });
    //document.title = document.title.replace(/\b(Ass)\b/g, 'A**');
    //document.title = document.title.replace(/\b(ass)\b/g, 'a**');
}());