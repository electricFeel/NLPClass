<!DOCTYPE html>
<html class="no-js">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>NLP Class Project</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width">

        <link rel="stylesheet" href="/css/bootstrap.min.css">
        <style>
            body {
                padding-top: 60px;
                padding-bottom: 40px;
            }
        </style>
        <link rel="stylesheet" href="/css/bootstrap-responsive.min.css">
        <link rel="stylesheet" href="/css/main.css">
    </head>
    <body>


        <header>
            <div class="container">
                <div class="row">
                <div class="span9 offset2">
                    <div clas="row">
                        <div class="topbox searchbox span3">
                            <h1>search</h1> 
                            <form class="form-search" action="topic">
                                <center>
                                  <div class="input-append">
                                    <input name="q" type="text" class="span2 search-query" placeholder="type your topic...">
                                    <button type="submit" class="btn"><i class="icon-search"></i> Search</button>
                                  </div>
                                </center>
                            </form>
                        </div>
                        <div class="topbox trending span4">
                            <h1>trending</h1> 
                            %for trend in trend_topics:
                                <a href="/topic?q={{ trend }}">{{ trend }}</a>
                            %end
                        </div>
                    </div>
                </div>
                </div>
            </div>
        </header>

        <div class="container">
            %if defined('topic'):
            <div class="row">
                <div class="span8 offset2">
                    <h2>{{ topic }}</h2>
                    <blockquote>
                        %for sent in sentences:
                            <span class="ref_sent" data-ref="{{ sent['from_article'] }}">{{ sent['sentence'] }}</span> 
                        %end
                    </blockquote>
                    
                    <hr/>

                    <h4>Related pages</h4>
                    <ol>
                        %for page in articles:
                            <li><a class="citation" target="_blank" href="{{ page }}">{{ page }}</a></li>
                        %end
                    </ol>
                </div>
            </div>
            %end

            <hr />
            
            <footer>
                <p>&copy; Lucas Sa and Omar Ayub 2013</p>
            </footer>

        </div> <!-- /container -->

        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script>window.jQuery || document.write('<script src="/js/vendor/jquery-1.9.1.min.js"><\/script>')</script>

        <script src="/js/vendor/bootstrap.min.js"></script>

        <script src="/js/main.js"></script>

        <script>
        $(function() {
            $(".ref_sent").hover(function() {
                $("a[href='" + $(this).attr("data-ref") + "']").addClass("ref_selected");
            });
            $(".ref_sent").mouseout(function() {
                $("a[href='" + $(this).attr("data-ref") + "']").removeClass("ref_selected");
            });
        });
        </script>
    </body>
</html>
