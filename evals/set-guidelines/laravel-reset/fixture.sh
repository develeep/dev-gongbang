mkdir -p app/Http/Controllers
cat > composer.json <<'JSON'
{
  "name": "acme/shop-admin",
  "type": "project",
  "require": { "php": "^8.2", "laravel/framework": "^11.0" },
  "autoload": { "psr-4": { "App\\": "app/" } }
}
JSON
cat > app/Http/Controllers/UserController.php <<'PHP'
<?php

namespace App\Http\Controllers;

use App\Models\User;

class UserController extends Controller
{
	public function index()
	{
		return view('users.index', array('users' => User::all()));
	}
}
PHP
cat > .php-cs-fixer.php <<'PHP'
<?php

return (new PhpCsFixer\Config())
    ->setIndent("\t")
    ->setRules(['@PSR2' => true, 'array_syntax' => ['syntax' => 'long']]);
PHP
cat > CLAUDE.md <<'MD'
# shop-admin

## 규칙

- 들여쓰기는 탭을 쓴다.
- 배열은 array() 문법을 쓴다.
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
