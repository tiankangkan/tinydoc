/**
 * Created by kangtian on 16/5/15.
 */

if ( CKEDITOR.env.ie && CKEDITOR.env.version < 9 )
    CKEDITOR.tools.enableHtml5Elements( document );
// The trick to keep the editor in the sample quite small
// unless user specified own height.

var initEditor = ( function() {
    CKEDITOR.editorConfig(CKEDITOR.config);

    var wysiwygareaAvailable = isWysiwygareaAvailable(),
        isBBCodeBuiltIn = !!CKEDITOR.plugins.get( 'bbcode' );

    return function() {
        var editorElement = CKEDITOR.document.getById( 'editor' );
        var my_editor;

        // :(((
        if ( isBBCodeBuiltIn ) {
            editorElement.setHtml(
                '<p>在这里编辑文本~\n\n' +
                '下方会在大约5秒延迟后, 显示出手写文本</p>'
            );
        }

        // Depending on the wysiwygare plugin availability initialize classic or inline editor.
        if ( wysiwygareaAvailable ) {
            my_editor = CKEDITOR.replace('editor', {
                customConfig : 'config.js'
            });
        } else {
            editorElement.setAttribute( 'contenteditable', 'true' );
            my_editor = CKEDITOR.inline( 'editor' );
            // TODO we can consider displaying some info box that
            // without wysiwygarea the classic editor may not work.
        }
        return my_editor;
    };

    function isWysiwygareaAvailable() {
        // If in development mode, then the wysiwygarea must be available.
        // Split REV into two strings so builder does not replace it :D.
        if ( CKEDITOR.revision == ( '%RE' + 'V%' ) ) {
            return true;
        }

        return !!CKEDITOR.plugins.get( 'wysiwygarea' );
    }
} )();